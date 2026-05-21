import { eq } from 'drizzle-orm'
import { v4 as uuidv4 } from 'uuid'
import { users, tickets, messages } from '@nuxthub/db/schema'
import { db } from '@nuxthub/db'

export default defineEventHandler(async (event) => {
  const sessionToken = getCookie(event, 'session_token')
  if (!sessionToken) throw createError({ statusCode: 401, message: 'Not logged in' })

  const user = await db.select().from(users).where(eq(users.session_token, sessionToken)).get()

  if (!user) throw createError({ statusCode: 404, message: 'User not found' })

  if (user.ticket_id) {
    throw createError({ statusCode: 400, message: 'Ticket already submited.' })
  }

  const adminUsername = `Administracja_${uuidv4().substring(0, 5)}`
  const botPassword = uuidv4()
  const botSessionToken = uuidv4()

  const botId = uuidv4()
  await db.insert(users).values({
    id: botId,
    username: adminUsername,
    password: botPassword,
    is_admin: true,
    session_token: botSessionToken
  }).execute()

  const ticketId = uuidv4()
  await db.insert(tickets).values({
    id: ticketId,
    admin_id: botId,
    is_accepted: false
  }).execute()

  await db.update(users).set({ ticket_id: ticketId }).where(eq(users.id, user.id)).execute()

  await db.insert(messages).values({
    id: uuidv4(),
    ticket_id: ticketId,
    sender: 'admin',
    content: `Dzień dobry. Przeglądam właśnie Twój wniosek. Proszę o szybkie doprecyzowanie Twojego doświadczenia zawodowego.`,
    created_at: new Date()
  }).execute()

  const host = getRequestHeader(event, 'host')
  const protocol = process.env.NODE_ENV === 'production' ? 'https' : 'http'

  setTimeout(async () => {
    try {
      await fetch(`${protocol}://${host}/admin/ticket/${ticketId}`, {
        headers: {
          Cookie: `session_token=${botSessionToken}`
        }
      })
    } catch { /* empty */ }
  }, 1000)

  setTimeout(async () => {
    try {
      const currentTicket = await db.select().from(tickets).where(eq(tickets.id, ticketId)).get()
      if (currentTicket && !currentTicket.is_accepted) {
        await db.insert(messages).values({
          id: uuidv4(),
          ticket_id: ticketId,
          sender: 'admin',
          content: 'Brak odpowiedzi w wymaganym czasie. Wniosek odrzucony, zamykam zgłoszenie.',
          created_at: new Date()
        }).execute()

        await db.update(tickets).set({ is_closed: 1 }).where(eq(tickets.id, ticketId)).execute()
      }
    } catch { /* empty */ }
  }, 60000)

  return { success: true, message: 'Wniosek złożony.' }
})
