import { eq, and } from 'drizzle-orm'
import { v4 as uuidv4 } from 'uuid'
import { users } from '@nuxthub/db/schema'
import { db } from '@nuxthub/db'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  if (!body.username || !body.password) {
    throw createError({ statusCode: 400, message: 'Missing username or password' })
  }

  const user = await db.select().from(users).where(
    and(eq(users.username, body.username), eq(users.password, body.password))
  ).get()

  if (user) {
    const sessionToken = uuidv4()
    await db.update(users).set({ session_token: sessionToken }).where(eq(users.id, user.id)).execute()

    setCookie(event, 'session_token', sessionToken, { httpOnly: true, secure: true })
    return { success: true }
  }

  throw createError({ statusCode: 401, message: 'Invalid credentials' })
})
