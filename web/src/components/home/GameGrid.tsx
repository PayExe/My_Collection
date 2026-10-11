import type { CSSProperties } from "react"
import { Link } from "react-router-dom"

import type { Item } from "../../types/api"
import { cubeColors } from "./cubeColors"

interface GameGridProps {
  games: Item[]
}

export function GameGrid({ games }: GameGridProps) {
  return (
    <div className="game-grid">
      {games.map((game, index) => {
        const colors = cubeColors[index % cubeColors.length]
        return <Link className="game-card" to={`/games/${game.id}`} key={game.id}>
          <div className="game-cover" style={{ backgroundColor: colors[0], "--card-delay": `${Math.min(index, 8) * 45}ms` } as CSSProperties}>
            <span className="game-number">{String(index + 1).padStart(2, "0")}</span>
            <span className="game-cube" style={{ "--cube-color": colors[1] } as CSSProperties} aria-hidden="true"><span className="cube-face cube-front" /><span className="cube-face cube-top" /><span className="cube-face cube-side" /></span>
            <strong>{game.titre}</strong>
          </div>
          <div className="game-card-meta"><strong>{game.titre}</strong><span>{game.categorie}</span></div>
        </Link>
      })}
    </div>
  )
}
