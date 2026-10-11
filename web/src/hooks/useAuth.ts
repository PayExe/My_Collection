import { useContext } from "react"

import { AuthContext } from "../contexts/auth-context"
import type { AuthContextValue } from "../contexts/auth-context"

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth doit être utilisé dans AuthProvider")
  }
  return context
}
