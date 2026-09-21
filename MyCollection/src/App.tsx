import { Navigate, Route, Routes } from "react-router-dom"

import { AuthPage } from "./pages/AuthPage"
import { GameEditPage } from "./pages/GameEditPage"
import { GamePage } from "./pages/GamePage"
import { NotFoundPage } from "./pages/NotFoundPage"

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<AuthPage mode="login" />} />
      <Route path="/register" element={<AuthPage mode="register" />} />
      <Route path="/games" element={<GamePage />} />
      <Route path="/game-edit" element={<GameEditPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export default App
