import { eq, asc } from 'drizzle-orm'
import { users, tickets, messages } from '@nuxthub/db/schema'
import { db } from '@nuxthub/db'

export default defineEventHandler(async (event) => {
  const sessionToken = getCookie(event, 'session_token')
  if (!sessionToken) throw createError({ statusCode: 401, message: 'Unauthorized' })

  const id = getRouterParam(event, 'id')
  if (!id) throw createError({ statusCode: 400, message: 'Missing ID' })

  const user = await db.select().from(users).where(eq(users.session_token, sessionToken)).get()
  if (!user) throw createError({ statusCode: 401, message: 'Unauthorized' })

  const ticket = await db.select().from(tickets).where(eq(tickets.id, id)).get()

  if (!ticket) {
    throw createError({ statusCode: 404, message: 'Not found' })
  }

  if (user.ticket_id !== id && ticket.admin_id !== user.id) {
    throw createError({ statusCode: 403, message: 'Forbidden' })
  }

  const ticketMessages = await db.select().from(messages)
    .where(eq(messages.ticket_id, id))
    .orderBy(asc(messages.created_at))

  return { ticket, messages: ticketMessages }
})
