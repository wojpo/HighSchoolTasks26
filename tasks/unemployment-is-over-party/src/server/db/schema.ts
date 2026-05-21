import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core'

export const users = sqliteTable('users', {
  id: text('id').primaryKey(),
  username: text('username').notNull().unique(),
  password: text('password').notNull(),
  ticket_id: text('ticket_id'),
  is_admin: integer('is_admin', { mode: 'boolean' }).default(false),
  session_token: text('session_token')
})

export const tickets = sqliteTable('tickets', {
  id: text('id').primaryKey(),
  admin_id: text('admin_id').references(() => users.id),
  is_accepted: integer('is_accepted', { mode: 'boolean' }).default(false),
  is_closed: integer('is_closed')
})

export const messages = sqliteTable('messages', {
  id: text('id').primaryKey(),
  ticket_id: text('ticket_id').references(() => tickets.id),
  sender: text('sender').notNull(),
  content: text('content').notNull(),
  created_at: integer('created_at', { mode: 'timestamp' }).notNull()
})
