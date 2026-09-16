import { HomePage } from "./pages/HomePage"
import { GamePage } from "./pages/GamePage"
import { NotFoundPage } from "./pages/NotFoundPage";
import { Route, Routes } from "react-router-dom";
import { GameEditPage } from "./pages/GameEditPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/games" element={<GamePage />} />
      <Route path="/game-edit" element={<GameEditPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export default App
