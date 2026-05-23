import { integer, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const containers = sqliteTable("containers", {
    id: text("id").primaryKey(),
    session: text("session").notNull(),
    createdAt: integer("created_at", { mode: "timestamp" }).notNull().$defaultFn(() => new Date()),
});
