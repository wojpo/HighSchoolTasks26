import { eq } from 'drizzle-orm'
import { users } from '@nuxthub/db/schema'
import { db } from '@nuxthub/db'

export default defineEventHandler(async (event) => {
  const sessionToken = getCookie(event, 'session_token')
  if (!sessionToken) return { user: null }

  const user = await db.select({
    id: users.id,
    username: users.username,
    is_admin: users.is_admin,
    ticket_id: users.ticket_id
  }).from(users).where(eq(users.session_token, sessionToken)).get()

  if (!user) return { user: null }
  return { user }
})
