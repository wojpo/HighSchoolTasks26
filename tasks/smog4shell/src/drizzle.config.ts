import { defineConfig } from "drizzle-kit";

export default defineConfig({
    dialect: "sqlite",
    schema: "./db/schema.ts",
    out: "./drizzle",
    dbCredentials: {
        url: process.env.SQLITE_DB_PATH ?? "./data/smog4shell.sqlite",
    },
});;
