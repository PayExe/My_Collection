import { createContext } from "react"

import type { User } from "../types/api"

export interface AuthContextValue {
  token: string | null
  user: User | null
  isLoading: boolean
  signIn: (accessToken: string) => Promise<void>
  signOut: () => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)
