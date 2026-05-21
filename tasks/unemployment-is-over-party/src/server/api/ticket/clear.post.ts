import { eq } from 'drizzle-orm'
import { users, tickets, messages } from '@nuxthub/db/schema'
import { db } from '@nuxthub/db'

export default defineEventHandler(async (event) => {
  const sessionToken = getCookie(event, 'session_token')
  if (!sessionToken) throw createError({ statusCode: 401, message: 'Unauthorized' })

  const user = await db.select().from(users).where(eq(users.session_token, sessionToken)).get()

  if (!user || !user.ticket_id) {
    return { success: true }
  }

  const ticketId = user.ticket_id

  const ticket = await db.select().from(tickets).where(eq(tickets.id, ticketId)).get()

  await db.update(users).set({ ticket_id: null }).where(eq(users.id, user.id)).execute()

  if (ticket) {
    await db.delete(messages).where(eq(messages.ticket_id, ticket.id)).execute()

    await db.delete(tickets).where(eq(tickets.id, ticket.id)).execute()

    if (ticket.admin_id) {
      await db.delete(users).where(eq(users.id, ticket.admin_id)).execute()
    }
  }

  return { success: true }
})
