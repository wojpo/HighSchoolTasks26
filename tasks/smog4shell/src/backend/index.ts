import express from "express"
import path from "path";
import Docker from "dockerode";
import { db } from "../db";
import {containers} from "../db/schema.ts";
import tar from "tar-fs";
import { eq } from "drizzle-orm"
import { migrate } from "drizzle-orm/node-postgres/migrator";

await migrate(db, { migrationsFolder: "./drizzle" });

const app = express()
app.use(express.json());
app.use(express.static(path.resolve( __dirname, "../frontend")));
app.set("trust proxy", 1);

const docker = new Docker({ socketPath: "/var/run/docker.sock" });

const IMAGE_NAME = "solr-log4shell-server";
const IMAGE_CONTEXT_DIR = path.resolve(process.cwd(), "flag-server");
const TARGET_NETWORK = "ctf-services-net";

async function imageExists(name: string): Promise<boolean> {
    try {
        await docker.getImage(name).inspect();
        return true;
    } catch (error: any) {
        if (error?.statusCode === 404) {
            return false;
        }
        throw error;
    }
}

async function buildImage(name: string, contextDir: string): Promise<void> {
    const pack = tar.pack(contextDir);
    await new Promise<void>((resolve, reject) => {
        docker.buildImage(pack, { t: name }, (error, stream) => {
            if (error || !stream) {
                reject(error ?? new Error("docker build stream unavailable"));
                return;
            }

            docker.modem.followProgress(stream, (err) => {
                if (err) {
                    reject(err);
                } else {
                    resolve();
                }
            });
        });
    });
}

async function ensureImage(name: string, contextDir: string): Promise<void> {
    if (await imageExists(name)) {
        return;
    }
    await buildImage(name, contextDir);
}

async function ensureNetwork(name: string): Promise<void> {
    try {
        await docker.getNetwork(name).inspect();
    } catch (error: any) {
        if (error?.statusCode === 404) {
            await docker.createNetwork({ Name: name });
            return;
        }
        throw error;
    }
}

async function isContainerRunning(id: string): Promise<boolean> {
    const name = `${id}-solr-log4shell-server`;
    try {
        const info = await docker.getContainer(name).inspect();
        return Boolean(info?.State?.Running);
    } catch (error: any) {
        if (error?.statusCode === 404) {
            return false;
        }
        throw error;
    }
}

async function run(ip: string | null) {
    const uuid = crypto.randomUUID().slice(0, 8);

    await ensureImage(IMAGE_NAME, IMAGE_CONTEXT_DIR);
    await ensureNetwork(TARGET_NETWORK);

    const container = await docker.createContainer({
        Image: IMAGE_NAME,
        name: `${uuid}-solr-log4shell-server`,

        ExposedPorts: {
            "8983/tcp": {},
        },

        HostConfig: {
            NetworkMode: TARGET_NETWORK,

            NanoCpus: 0.5e9,          // 0.5 vCPU (wartość w nanosekundach CPU/s)

            // RAM
            Memory: 1024 * 1024 * 1024,       // 1 GB twardy limit
            MemorySwap: 1024 * 1024 * 1024,   // wyłącza swap (= Memory → brak swapu)
            MemoryReservation: 512 * 1024 * 1024, // soft limit (scheduler hint)

            // /dev/shm for JVM shared memory
            ShmSize: 256 * 1024 * 1024,

            // Procesy
            PidsLimit: 100,

            // File descriptor limits for Solr
            Ulimits: [
                { Name: "nofile", Soft: 65000, Hard: 65000 },
            ],
        },

        Labels: {
            "traefik.enable": "true",

            [`traefik.http.routers.solr-${uuid}.rule`]:
                `Host(\`${uuid}.solr.hack4krak.pl\`)`,

            [`traefik.http.routers.solr-${uuid}.entrypoints`]:
                "solr",

            [`traefik.http.services.solr-${uuid}.loadbalancer.server.port`]:
                "8983",
        },
    });


    await container.start();

    const TIMEOUT_MS = 60 * 60 * 1000;

    setTimeout(async () => {
        try {
            await container.remove({ force: true });
        } catch {}
    }, TIMEOUT_MS);

    await db.insert(containers).values({
        id: uuid,
        user_ip: ip,
        createdAt: new Date(),
    });

    return uuid;

}

app.post("/api/create", async (req, res) => {
    try {
        let ip = req.ip;
        if (ip !== undefined) {
            const container = await db
                .select()
                .from(containers)
                .where(eq(containers.user_ip, ip))
                .limit(1);
            if (container.length > 0 && container[0]) {
                const existingId = container[0].id;
                if (existingId && await isContainerRunning(existingId)) {
                    return res.json({
                        url: existingId + ".solr.hack4krak.pl",
                    });
                }
                const uuid = await run(ip)
                await db.update(containers)
                    .set({ id: uuid, createdAt: new Date() })
                    .where(eq(containers.user_ip, ip));
                return res.json({
                    url: uuid + ".solr.hack4krak.pl",
                });
            } else {
                const uuid = await run(ip)
                return res.json({
                    url: uuid + ".solr.hack4krak.pl",
                });
            }

        } else {
            const uuid = await run(null)
            return res.json({
                url: uuid + ".solr.hack4krak.pl",
            });
        }
    } catch (error) {
        console.error("Error creating container:", error);
        res.status(500).json({ error: "Internal server error" });
    }

})

app.listen(3000, () => {
    console.log(`Server running on port 3000`)
})