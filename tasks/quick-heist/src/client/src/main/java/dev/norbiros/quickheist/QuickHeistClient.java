package dev.norbiros.quickheist;

import net.fabricmc.api.ClientModInitializer;
import net.minecraft.client.Minecraft;

public class QuickHeistClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        Thread thread = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                Minecraft minecraft = Minecraft.getInstance();
                if (minecraft != null) minecraft.execute(() -> HeistTeleport.tick(minecraft));

                try {
                    Thread.sleep(50);
                } catch (InterruptedException exception) {
                    Thread.currentThread().interrupt();
                }
            }
        }, "quick-heist-tp");
        thread.setDaemon(true);
        thread.start();
    }
}
