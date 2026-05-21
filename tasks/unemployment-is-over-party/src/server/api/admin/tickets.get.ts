import { users, tickets } from '@nuxthub/db/schema'
import { db } from '@nuxthub/db'
import { eq } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
  const sessionToken = getCookie(event, 'session_token')
  if (!sessionToken) throw createError({ statusCode: 401, message: 'Unauthorized' })

  const user = await db.select().from(users).where(eq(users.session_token, sessionToken)).get()

  if (!user || !user.is_admin) throw createError({ statusCode: 403, message: 'Forbidden' })

  const allTickets = await db
    .select({
      id: tickets.id,
      is_accepted: tickets.is_accepted,
      username: users.username
    })
    .from(tickets)
    .leftJoin(users, eq(tickets.id, users.ticket_id))
    .where(eq(tickets.admin_id, user.id))
    .all()

  return { tickets: allTickets }
})
