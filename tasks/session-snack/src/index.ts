import express from "express"
import { z } from "zod"
import cookieParser from "cookie-parser"
import fs from "fs"
import path from "path";

const app = express()
app.use(express.json());
app.use(cookieParser());
app.use("/styles", express.static(path.resolve("frontend", "styles")));

const loginSchema = z.object({
    username: z.string(),
    password: z.string(),
})
const cookiesSchema = z.object({
    username:  z.string(),
    isAdmin: z.boolean(),
})

function requireSession(session: string){
    if(!session){
        return undefined
    }
    let sessionData
    try {
        sessionData = cookiesSchema.parse(JSON.parse(Buffer.from(session, "base64").toString("utf-8")))
    }
    catch(err) {
        return undefined
    }
    return sessionData
}

app.post("/api/login", (req, res) => {
    const body = req.body
    const parsedBody = loginSchema.safeParse(body)
    if (!parsedBody.success) {
        return res.status(400).json({error: "Invalid request"})
    }
    const { username, password } = parsedBody.data
    if (username === "kanarzyca_halina" && password === "bil3c1kPr0sze!!") {
        const cookie = {
            username: username,
            isAdmin: false,
        }
        const encodedCookie = Buffer.from(JSON.stringify(cookie)).toString("base64")
        res.cookie("session", encodedCookie, {
            maxAge: 1000 * 60 * 60 // 1 hour
        });
        return res.status(200).json({ok: true})
    }
    return res.status(401).json({error: "Invalid credentials"})
})

app.get("/api/flag", (req, res) => {
    const { isAdmin } = requireSession(req.cookies.session) || {}
    if (isAdmin) {
        return res.status(200).json({flag: "hack4KrakCTF{cook1e5ar38As36A3nc0ded}"})
    }
    return res.status(403).json({error: "Invalid user"})
})

app.get("/admin", async (req, res) => {
    const { isAdmin, username } = requireSession(req.cookies.session) || {}
    if(!username){
        return res.status(401).sendFile(path.resolve("frontend/public", "401.html"))
    }else if(!isAdmin){
        return res.status(403).sendFile(path.resolve("frontend/public", "403.html"))
    }

    try {
        const real = await fs.promises.realpath(path.resolve("frontend/admin", "admin.html"))
        return res.sendFile(real)
    }
    catch {
        return res.status(404).sendFile(path.resolve("frontend/public", "404.html"))
    }
})

app.get("/admin.js", async (req, res) => {
    const { isAdmin, username } = requireSession(req.cookies.session) || {}
    if(!username){
        return res.status(401).sendFile(path.resolve("frontend/public", "401.html"))
    }else if(!isAdmin){
        return res.status(403).sendFile(path.resolve("frontend/public", "403.html"))
    }

    try {
        const real = await fs.promises.realpath(path.resolve("frontend/admin", "admin.js"))
        return res.sendFile(real)
    }
    catch {
        return res.status(404).sendFile(path.resolve("frontend/public", "404.html"))
    }
})

app.get("/app/:asset", async (req, res) => {
    if (!requireSession(req.cookies.session)) {
        return res.status(401).sendFile(path.resolve("frontend/public", "401.html"))
    }

    const base = path.resolve("frontend", "app")

    let filePath
    if (path.extname(req.params.asset) === "") {
        filePath = path.resolve("frontend/app", `${req.params.asset}.html`)
    }
    else {
        filePath = path.resolve("frontend/app", `${req.params.asset}`)
    }

    try {
        const real = await fs.promises.realpath(filePath)
        if(path.relative(base, real).startsWith("..")){
            return res.status(404).sendFile(path.resolve("frontend/public", "404.html"))
        }
        return res.sendFile(real)
    }
    catch {
        return res.status(404).sendFile(path.resolve("frontend/public", "404.html"))
    }
})

app.get("/", async (req, res) => {

    try {
        const filePath = path.resolve("frontend/public", "index.html")
        await fs.promises.access(filePath)
        return res.sendFile(filePath)
    }
    catch {
        return res.status(404).sendFile(path.resolve("frontend/public", "404.html"))
    }
})

app.get("/:asset", async (req, res) => {
    const base = path.resolve("frontend", "public")

    let filePath
    if (path.extname(req.params.asset) === "") {
        filePath = path.resolve("frontend/public", `${req.params.asset}.html`)
    }
    else {
        filePath = path.resolve("frontend/public", `${req.params.asset}`)
    }

    try {
        const real = await fs.promises.realpath(filePath)
        if(path.relative(base, real).startsWith("..")){
            return res.status(404).sendFile(path.resolve("frontend/public", "404.html"))
        }
        return res.sendFile(real)
    }
    catch {
        return res.status(404).sendFile(path.resolve("frontend/public", "404.html"))
    }
})

app.listen(3000, () => {
    console.log(`Server running on port 3000`)
})