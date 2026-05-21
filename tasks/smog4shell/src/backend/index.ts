import express from "express"
import path from "path";
import Docker from "dockerode";
import { db } from "../db";
import {containers} from "../db/schema.ts";
import { fileURLToPath } from "url";
import { eq, lte } from "drizzle-orm"
import { migrate } from "drizzle-orm/node-postgres/migrator";
import crypto from "crypto";
import z from "zod"
import cookieParser from "cookie-parser"
import tar from "tar-fs"
let buildPromise: Promise<void> | null = null;

async function migrateWithRetry() {
    let lastError: unknown;
    for (let attempt = 1; attempt <= 30; attempt++) {
        try {
            await migrate(db, { migrationsFolder: "./drizzle" });
            return;
        } catch (error) {
            lastError = error;
            await new Promise((resolve) => setTimeout(resolve, 1000));
        }
    }
    throw lastError;
}

await migrateWithRetry();
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const app = express()
app.use(express.json());
app.use(cookieParser());
app.use(express.static(path.resolve( __dirname, "../frontend")));
app.use(express.static(path.resolve( __dirname, "../frontend/assets")));
app.set("trust proxy", 1);

const cookiesSchema = z.object({
    sessionId: z.string(),
})

const docker = new Docker({ socketPath: "/var/run/docker.sock" });

const IMAGE_NAME = "solr-log4shell-server";
const CONTAINER_SUFFIX = "-solr-log4shell-server";
const SOLR_HOST_SUFFIX = "-solr.hack4krak.pl";
const IMAGE_CONTEXT_DIR = path.resolve(process.cwd(), "flag-server");
const TARGET_NETWORK = "bridge";
const TIMEOUT_MS = Number(process.env.INSTANCE_TIMEOUT_MS ?? String(5 * 60 * 1000));
const MAX_ACTIVE_CONTAINERS = Number(process.env.MAX_ACTIVE_CONTAINERS ?? "10");
let createQueue: Promise<void> = Promise.resolve();

async function withCreateLock<T>(fn: () => Promise<T>): Promise<T> {
    const previous = createQueue;
    let release!: () => void;
    createQueue = new Promise<void>((resolve) => {
        release = resolve;
    });
    await previous;
    try {
        return await fn();
    } finally {
        release();
    }
}

async function cleanupExpiredContainers() {
    const expiredAt = new Date(Date.now() - TIMEOUT_MS);
    let expired: typeof containers.$inferSelect[] = [];
    try {
        expired = await db
            .select()
            .from(containers)
            .where(lte(containers.createdAt, expiredAt));
    } catch(error){}
    for (const c of expired) {
        try {
            await docker.getContainer(`${c.id}-solr-log4shell-server`).remove({ force: true });
        } catch (e) { console.error("Failed to remove container:", e); }
        await db.delete(containers).where(eq(containers.id, c.id));
    }
}

async function cleanupAllSolrContainers() {
    let allContainers: any[] = [];
    try {
        allContainers = await docker.listContainers({ all: true });
    } catch (error) {
        console.error("Failed to list containers for cleanup:", error);
        return;
    }

    for (const c of allContainers) {
        const names = c.Names ?? [];
        if (!names.some((name: string) => name.slice(1).endsWith(CONTAINER_SUFFIX))) {
            continue;
        }

        try {
            await docker.getContainer(c.Id).remove({ force: true });
        } catch (error) {
            console.error(`Failed to remove Solr container ${c.Id}:`, error);
        }
    }

    try {
        await db.delete(containers);
    } catch (error) {
        console.error("Failed to clear Solr container records:", error);
    }
}


await cleanupAllSolrContainers();
await cleanupExpiredContainers();
setInterval(cleanupExpiredContainers, 5 * 60 * 1000);

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

    return new Promise<void>((resolve, reject) => {
        docker.buildImage(pack, { t: name }, async (error, stream) => {
            if (error || !stream) {
                reject(error ?? new Error("docker build stream unavailable"));
                return;
            }

            try {
                await docker.modem.followProgress(stream, (err) => {
                    if (err) reject(err);
                    else resolve();
                });
            } catch (err) {
                reject(err);
            }
        });
    });
}

async function ensureImage(name: string, contextDir: string): Promise<void> {
    if (await imageExists(name)) {
        console.log(`Docker image ${name} already exists`);
        return;
    }

    if (!buildPromise) {
        console.log(`Building Docker image ${name}`);
        buildPromise = buildImage(name, contextDir).finally(() => {
            buildPromise = null;
        });
    }

    await buildPromise;
    console.log(`Docker image ${name} is ready`);
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
    const name = `${id}${CONTAINER_SUFFIX}`;
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

async function getActiveContainerCount(): Promise<number> {
    const knownContainers = await db.select().from(containers);
    let activeCount = 0;

    for (const knownContainer of knownContainers) {
        if (await isContainerRunning(knownContainer.id)) {
            activeCount += 1;
        } else {
            await db.delete(containers).where(eq(containers.id, knownContainer.id));
        }
    }

    return activeCount;
}

async function run(session: string) {
    const uuid = crypto.randomUUID().slice(0, 8);

    console.log(`Creating Solr instance ${uuid} for session ${session}`);
    await ensureImage(IMAGE_NAME, IMAGE_CONTEXT_DIR);
    console.log(`Ensuring Docker network ${TARGET_NETWORK}`);
    await ensureNetwork(TARGET_NETWORK);

    console.log(`Creating container ${uuid}${CONTAINER_SUFFIX}`);
    const container = await docker.createContainer({
        Image: IMAGE_NAME,
        name: `${uuid}${CONTAINER_SUFFIX}`,
        Env: ["SOLR_JAVA_MEM=-Xms128m -Xmx384m"],

        ExposedPorts: {
            "8983/tcp": {},
        },

        HostConfig: {
            NetworkMode: TARGET_NETWORK,

            NanoCpus: 0.5e9,          // 0.5 vCPU (wartość w nanosekundach CPU/s)

            // RAM
            Memory: 512 * 1024 * 1024,
            MemorySwap: 512 * 1024 * 1024,
            MemoryReservation: 256 * 1024 * 1024,

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
                `Host(\`${uuid}${SOLR_HOST_SUFFIX}\`)`,

            [`traefik.http.routers.solr-${uuid}.entrypoints`]:
                "solr",

            [`traefik.http.services.solr-${uuid}.loadbalancer.server.port`]:
                "8983",
        },
    });


    await container.start();
    console.log(`Started container ${uuid}${CONTAINER_SUFFIX}`);


    setTimeout(async () => {
        try {
            await container.remove({force: true});
            await db.delete(containers).where(eq(containers.id, uuid));
        } catch (e) {
            console.error("Failed to remove container:", e);
        }
    }, TIMEOUT_MS);


    await db.insert(containers).values({
        id: uuid,
        session: session,
        createdAt: new Date(),
    });

    console.log(`Registered Solr instance ${uuid}`);
    return uuid;

}

app.post("/api/login", async (req, res) => {
    if(req.cookies.session){
        return res.json({ok: true})
    } else {
        let sessionId = crypto.randomUUID()
        let cookie = JSON.stringify({sessionId: sessionId})
        res.cookie("session", cookie)
        return res.json({ok: true})
    }
})

app.post("/api/create", async (req, res) => {
    try {
        return await withCreateLock(async () => {
            const rawSession = req.cookies.session
            if(!rawSession){
                return res.status(400).json({ error: "Cookie required"})
            }
            let jsonParsedSession
            try {
                jsonParsedSession = JSON.parse(rawSession)
            } catch {
                return res.status(400).json({ error: "Invalid session cookie" })
            }
            let parsedSession = cookiesSchema.safeParse(jsonParsedSession)
            if(!parsedSession.success){
                return res.status(400).json({ error: "Invalid session cookie" });
            }
            const SESSION = parsedSession.data
            let userContainers = await db
                .select()
                .from(containers)
                .where(eq(containers.session, SESSION.sessionId));

            let userDomainId = null
            for (let userContainer of userContainers){
                if(await isContainerRunning(userContainer.id)){
                    userDomainId = userContainer.id
                }else{
                    await db
                        .delete(containers)
                        .where(eq(containers.id, userContainer.id));
                }
            }

            if(userDomainId) {
                return res.json({url: `${userDomainId}${SOLR_HOST_SUFFIX}`, ttlSeconds: Math.floor(TIMEOUT_MS / 1000)})
            }

            const activeContainerCount = await getActiveContainerCount();
            if (activeContainerCount >= MAX_ACTIVE_CONTAINERS) {
                console.error(
                    `Active Solr container limit reached: ${activeContainerCount}/${MAX_ACTIVE_CONTAINERS}`,
                );
                return res.status(429).json({
                    error: "Too many active instances are running. Please contact the administrators.",
                });
            }

            const newId = await run(SESSION.sessionId)
            return res.json({url: `${newId}${SOLR_HOST_SUFFIX}`, ttlSeconds: Math.floor(TIMEOUT_MS / 1000)})
        });
    } catch (error) {
        console.error("Failed to create container:", error);
        return res.status(500).json({ error: "Failed to create instance" });
    }

})

async function shutdown(signal: NodeJS.Signals) {
    console.log(`Received ${signal}, cleaning up Solr containers`);
    await cleanupAllSolrContainers();
    process.exit(0);
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

app.listen(3000, () => {
    console.log(`Server running on port 3000`)
})
