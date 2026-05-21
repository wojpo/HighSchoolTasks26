// VULNERABILITY: Module-level state leak!
// This object is shared across all concurrent requests in the Node process.
const activeUsersObj: Ref<Record<string, string>> = ref({})

export const useAuthState = () => {
  const state = useState<Record<string, string>>('leaked_users_state', () => activeUsersObj)

  const setCurrentUser = (solverId: string, username: string) => {
    state.value[solverId] = username
    activeUsersObj.value[solverId] = username
  }

  const getCurrentUser = (solverId: string) => {
    return state.value[solverId] || null
  }

  return {
    setCurrentUser,
    getCurrentUser
  }
}
