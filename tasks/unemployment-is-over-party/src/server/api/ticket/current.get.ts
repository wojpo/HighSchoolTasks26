import { eq, asc } from 'drizzle-orm'
import { users, tickets, messages } from '@nuxthub/db/schema'
import { db } from '@nuxthub/db'

export default defineEventHandler(async (event) => {
  const sessionToken = getCookie(event, 'session_token')
  if (!sessionToken) {
    throw createError({ statusCode: 401, message: 'Unauthorized' })
  }

  const user = await db.select().from(users).where(eq(users.session_token, sessionToken)).get()

  if (!user || !user.ticket_id) {
    return { ticket: null, messages: [] }
  }

  const ticket = await db.select().from(tickets).where(eq(tickets.id, user.ticket_id)).get()

  if (!ticket) {
    await db.update(users).set({ ticket_id: null }).where(eq(users.id, user.id)).execute()
    return { ticket: null, messages: [] }
  }

  const ticketMessages = await db.select().from(messages)
    .where(eq(messages.ticket_id, ticket.id))
    .orderBy(asc(messages.created_at))

  return { ticket, messages: ticketMessages }
})
