import { users, tickets, messages } from '@nuxthub/db/schema'
import { db } from '@nuxthub/db'
import { eq } from 'drizzle-orm'
import { v4 as uuidv4 } from 'uuid'

export default defineEventHandler(async (event) => {
  const sessionToken = getCookie(event, 'session_token')
  if (!sessionToken) throw createError({ statusCode: 401, message: 'Unauthorized' })

  const user = await db.select().from(users).where(eq(users.session_token, sessionToken)).get()

  if (!user || !user.is_admin) throw createError({ statusCode: 403, message: 'Forbidden' })

  const body = await readBody(event)
  const ticketId = body.ticket_id

  if (!ticketId) {
    throw createError({ statusCode: 400, message: 'Missing ticket ID' })
  }

  const ticket = await db.select().from(tickets).where(eq(tickets.id, ticketId)).get()
  if (!ticket) {
    throw createError({ statusCode: 404, message: 'Ticket not found' })
  }

  if (ticket.admin_id !== user.id) {
    throw createError({ statusCode: 403, message: 'You have no permission to accept this ticket.' })
  }

  if (ticket.is_closed) {
    throw createError({ statusCode: 400, message: 'Ticket is already closed' })
  }

  await db.update(tickets).set({ is_accepted: true }).where(eq(tickets.id, ticketId)).execute()

  await db.insert(messages).values({
    id: uuidv4(),
    ticket_id: ticketId,
    sender: 'admin',
    content: 'Gratulacje! Twój wniosek został rozpatrzony pozytywnie. Twój login do systemu: Hack4KrakCTF{H3LLO-I-W0ULD-L1K3-T0-4PPLY}',
    created_at: new Date()
  }).execute()

  return { success: true }
})
