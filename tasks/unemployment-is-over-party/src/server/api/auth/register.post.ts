import { eq } from 'drizzle-orm'
import { v4 as uuidv4 } from 'uuid'
import { users } from '@nuxthub/db/schema'
import { db } from '@nuxthub/db'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  if (!body.username || !body.password) {
    console.log(body)
    throw createError({ statusCode: 400, message: 'Missing username or password' })
  }

  const existing = await db.select().from(users).where(eq(users.username, body.username)).get()
  if (existing) {
    console.log(existing)
    throw createError({ statusCode: 400, message: 'Username already exists' })
  }

  const userId = uuidv4()
  const sessionToken = uuidv4()
  console.log(`Creating user ${body.username} with id ${userId} and session token ${sessionToken}`)
  const result = await db.insert(users).values({
    id: userId,
    username: body.username,
    password: body.password,
    session_token: sessionToken,
    ticket_id: null
  }).execute()
  console.log(result)

  setCookie(event, 'session_token', sessionToken, { httpOnly: true, secure: true })

  return { success: true }
})
