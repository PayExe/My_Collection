import { Navigate, Route, Routes } from "react-router-dom"

import { AuthPage } from "./pages/AuthPage"
import { ProtectedRoute } from "./components/ProtectedRoute"
import { GameEditPage } from "./pages/GameEditPage"
import { GamePage } from "./pages/GamePage"
import { HomePage } from "./pages/HomePage"
import { NotFoundPage } from "./pages/NotFoundPage"

function App() {
  return (
    <Routes>
      <Route path="/" element={<AuthPage mode="login" />} />
      <Route path="/login" element={<Navigate to="/" replace />} />
      <Route path="/register" element={<AuthPage mode="register" />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/home" element={<HomePage />} />
        <Route path="/games" element={<GamePage />} />
        <Route path="/game-edit" element={<GameEditPage />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export default App
