import { Navigate, Route, Routes } from "react-router-dom"

import { AuthPage } from "./pages/AuthPage"
import { ProtectedRoute } from "./components/ProtectedRoute"
import { GameEditPage } from "./pages/GameEditPage"
import { GamePage } from "./pages/GamePage"
import { GameDetailPage } from "./pages/GameDetailPage"
import { HomePage } from "./pages/HomePage"
import { NotFoundPage } from "./pages/NotFoundPage"
import { CollectionPage } from "./pages/CollectionPage"
import { StatsPage } from "./pages/StatsPage"

function App() {
  return (
    <Routes>
      <Route path="/" element={<AuthPage mode="login" />} />
      <Route path="/login" element={<Navigate to="/" replace />} />
      <Route path="/register" element={<AuthPage mode="register" />} />
      <Route path="/games" element={<GamePage />} />
      <Route path="/games/:itemId" element={<GameDetailPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/home" element={<HomePage />} />
        <Route path="/collection" element={<CollectionPage />} />
        <Route path="/stats" element={<StatsPage />} />
        <Route path="/game-edit" element={<GameEditPage />} />
        <Route path="/game-edit/:entryId" element={<GameEditPage />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export default App
