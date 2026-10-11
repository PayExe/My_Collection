import { useState } from "react"

interface GameCoverProps {
  src: string
  title: string
  className?: string
}

export function GameCover({ src, title, className = "game-cover-image" }: GameCoverProps) {
  const [hasFailed, setHasFailed] = useState(false)

  if (hasFailed) return null

  return (
    <img
      className={className}
      src={src}
      alt={`Jaquette de ${title}`}
      loading="lazy"
      onError={() => setHasFailed(true)}
    />
  )
}
