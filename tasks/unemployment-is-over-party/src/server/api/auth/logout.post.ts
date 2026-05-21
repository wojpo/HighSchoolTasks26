import { eq } from 'drizzle-orm'
import { db } from '@nuxthub/db'
import { users } from '@nuxthub/db/schema'

export default defineEventHandler(async (event) => {
  const sessionToken = getCookie(event, 'session_token')
  if (sessionToken) {
    await db.update(users).set({ session_token: null }).where(eq(users.session_token, sessionToken)).execute()
  }

  setCookie(event, 'session_token', '', { maxAge: -1, httpOnly: true, secure: true })

  return { success: true }
})
