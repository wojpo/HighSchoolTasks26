import { pgTable, text, timestamp } from "drizzle-orm/pg-core";

export const containers = pgTable("containers", {
    id: text("id").primaryKey(),
    user_ip: text("user_ip"),
    createdAt: timestamp("created_at").notNull().defaultNow(),
});