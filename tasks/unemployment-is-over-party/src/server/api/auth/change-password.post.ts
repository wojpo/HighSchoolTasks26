import { eq } from 'drizzle-orm'
import { users } from '@nuxthub/db/schema'
import { db } from '@nuxthub/db'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  const targetUsername = body.username
  const newPassword = body.new_password

  if (!targetUsername || !newPassword) {
    throw createError({ statusCode: 400, message: 'Missing username or new password' })
  }

  const user = await db.select().from(users).where(eq(users.username, targetUsername)).get()
  if (user) {
    await db.update(users).set({ password: newPassword }).where(eq(users.username, targetUsername)).execute()
    return { success: true, message: 'Password changed successfully' }
  }

  throw createError({ statusCode: 404, message: 'User not found' })
})
