package dev.norbiros.quickheist;

import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.network.protocol.game.ServerboundMovePlayerPacket;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

import java.lang.reflect.Method;

public final class HeistTeleport {
    private static final double STEP_DISTANCE = 50;
    private static final int GLFW_KEY_K = 75;
    private static final int GLFW_PRESS = 1;
    private static boolean wasPressed;

    private HeistTeleport() {
    }

    public static void tick(Minecraft minecraft) {
        if (minecraft.player == null || minecraft.level == null || minecraft.gameMode == null) return;

        boolean pressed = isKPressed(minecraft);
        if (!pressed || wasPressed) {
            wasPressed = pressed;
            return;
        }

        wasPressed = true;
        run(minecraft);
    }

    private static void run(Minecraft minecraft) {
        LocalPlayer player = minecraft.player;
        Vec3 start = player.position();
        Vec3 forward = horizontalForward(player).scale(STEP_DISTANCE);
        Vec3 up = start.add(0, STEP_DISTANCE, 0);
        Vec3 front = up.add(forward);
        Vec3 target = front.add(0, -STEP_DISTANCE, 0);
        player.setDeltaMovement(Vec3.ZERO);
        flushGroundTicks(player);
        sendPosition(player, up);
        sendPosition(player, front);
        sendPosition(player, target);
        player.setPos(target.x, target.y, target.z);

        Entity entity = findTarget(minecraft, target);
        if (entity != null) {
            minecraft.gameMode.attack(player, entity);
        }
    }

    private static Vec3 horizontalForward(LocalPlayer player) {
        float radians = (float) Math.toRadians(player.getYRot());
        return new Vec3(-Math.sin(radians), 0, Math.cos(radians)).normalize();
    }

    private static Entity findTarget(Minecraft minecraft, Vec3 targetPosition) {
        Entity closest = null;
        double closestDistance = 36;

        for (Entity entity : minecraft.level.entitiesForRendering()) {
            if (entity == minecraft.player || !entity.isAlive() || !entity.isAttackable()) continue;

            double distance = entity.distanceToSqr(targetPosition);
            if (distance < closestDistance) {
                closestDistance = distance;
                closest = entity;
            }
        }

        return closest;
    }

    private static void flushGroundTicks(LocalPlayer player) {
        for (int i = 0; i < 18; i++) {
            player.connection.send(new ServerboundMovePlayerPacket.StatusOnly(true, false));
        }
    }

    private static void sendPosition(LocalPlayer player, Vec3 position) {
        player.connection.send(new ServerboundMovePlayerPacket.Pos(position, true, false));
    }

    private static boolean isKPressed(Minecraft minecraft) {
        try {
            Class<?> glfw = Class.forName("org.lwjgl.glfw.GLFW");
            Method glfwGetKey = glfw.getMethod("glfwGetKey", long.class, int.class);
            Object result = glfwGetKey.invoke(null, minecraft.getWindow().getWindow(), GLFW_KEY_K);
            return result instanceof Integer keyState && keyState == GLFW_PRESS;
        } catch (ReflectiveOperationException exception) {
            System.out.println("Cannot access GLFW key state: " + exception.getClass().getSimpleName());
            return false;
        }
    }
}
