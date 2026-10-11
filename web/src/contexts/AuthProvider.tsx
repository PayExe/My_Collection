import {
  useEffect,
  useState,
  type ReactNode,
} from "react"

import { AuthContext } from "./auth-context"
import { getCurrentUser } from "../services/authService"
import type { AuthContextValue } from "./auth-context"

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem("access_token"),
  )
  const [user, setUser] = useState<AuthContextValue["user"]>(null)
  const [isLoading, setIsLoading] = useState(() =>
    Boolean(localStorage.getItem("access_token")),
  )

  useEffect(() => {
    const savedToken = localStorage.getItem("access_token")
    if (!savedToken) {
      return
    }

    getCurrentUser()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("access_token")
        setToken(null)
        setUser(null)
      })
      .finally(() => setIsLoading(false))
  }, [])

  async function signIn(accessToken: string): Promise<void> {
    localStorage.setItem("access_token", accessToken)
    setToken(accessToken)
    setUser(await getCurrentUser())
  }

  function signOut(): void {
    localStorage.removeItem("access_token")
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ token, user, isLoading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}
