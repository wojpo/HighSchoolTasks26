import { eq } from 'drizzle-orm'
import { v4 as uuidv4 } from 'uuid'
import { users, tickets, messages } from '@nuxthub/db/schema'
import { db } from '@nuxthub/db'

export default defineEventHandler(async (event) => {
  const sessionToken = getCookie(event, 'session_token')
  if (!sessionToken) throw createError({ statusCode: 401, message: 'Unauthorized' })

  const user = await db.select().from(users).where(eq(users.session_token, sessionToken)).get()
  if (!user || !user.ticket_id) {
    throw createError({ statusCode: 403, message: 'Forbidden' })
  }

  const ticketId = user.ticket_id

  const ticket = await db.select().from(tickets).where(eq(tickets.id, ticketId)).get()

  if (!ticket) throw createError({ statusCode: 404, message: 'Ticket not found' })

  const body = await readBody(event)
  if (!body.content) throw createError({ statusCode: 400, message: 'Empty message' })

  await db.insert(messages).values({
    id: uuidv4(),
    ticket_id: ticketId,
    sender: 'user',
    content: body.content,
    created_at: new Date()
  }).execute()

  await db.insert(messages).values({
    id: uuidv4(),
    ticket_id: ticketId,
    sender: 'admin',
    content: 'Odrzucam podanie. Niestety nie spełniasz naszych wymagań. Zamykam zgłoszenie.',
    created_at: new Date()
  }).execute()

  await db.update(tickets).set({ is_closed: 1 }).where(eq(tickets.id, ticketId)).execute()

  return { success: true }
})
