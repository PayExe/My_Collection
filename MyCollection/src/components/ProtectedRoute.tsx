import { Navigate, Outlet } from "react-router-dom"

import { useAuth } from "../hooks/useAuth"

export function ProtectedRoute() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <p className="route-loading">Vérification de la session...</p>
  }

  if (!user) {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
