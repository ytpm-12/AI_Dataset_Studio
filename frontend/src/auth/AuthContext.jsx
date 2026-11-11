import { useEffect, useMemo, useState } from 'react'

import { api } from '../api/client'
import AuthContext from './context'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.currentUser()
      .then(setUser)
      .catch((error) => {
        if (error.status !== 403) console.error(error)
      })
      .finally(() => setLoading(false))
  }, [])

  const value = useMemo(() => ({
    user,
    loading,
    async login(credentials) {
      const authenticatedUser = await api.login(credentials)
      setUser(authenticatedUser)
      return authenticatedUser
    },
    async register(values) {
      const authenticatedUser = await api.register(values)
      setUser(authenticatedUser)
      return authenticatedUser
    },
    async logout() {
      await api.logout()
      setUser(null)
    },
  }), [loading, user])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
