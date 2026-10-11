import { Link } from "react-router-dom"

import type { Item } from "../../types/api"
import { cubeColors } from "./cubeColors"
import { ArrowIcon } from "./HomeIcons"

interface FeaturedCarouselProps {
  games: Item[]
  activeSlide: number
  onSlideChange: (index: number) => void
}

export function FeaturedCarousel({ games, activeSlide, onSlideChange }: FeaturedCarouselProps) {
  const featuredGame = games[activeSlide % Math.max(games.length, 1)]
  if (!featuredGame) return null

  function changeSlide(direction: "previous" | "next") {
    onSlideChange(direction === "next"
      ? (activeSlide + 1) % games.length
      : (activeSlide - 1 + games.length) % games.length)
  }

  return (
    <section className="featured-section" aria-label="Jeu mis en avant">
      <button className="carousel-arrow carousel-arrow-left" type="button" onClick={() => changeSlide("previous")} aria-label="Jeu précédent"><ArrowIcon direction="left" /></button>
      <div className="featured-card" style={{ backgroundColor: cubeColors[activeSlide % cubeColors.length][0] }}>
        <div className="featured-copy" key={featuredGame.id}>
          <p className="card-kicker">Choix du moment · {featuredGame.categorie}</p>
          <h1>{featuredGame.titre}</h1>
          <p>{featuredGame.description}</p>
          <Link className="featured-link" to={`/games/${featuredGame.id}`}>Découvrir le jeu <span aria-hidden="true">↗</span></Link>
        </div>
      </div>
      <button className="carousel-arrow carousel-arrow-right" type="button" onClick={() => changeSlide("next")} aria-label="Jeu suivant"><ArrowIcon direction="right" /></button>
      <div className="carousel-dots" aria-label="Sélection du jeu mis en avant">
        {games.slice(0, 6).map((game, index) => <button className={index === activeSlide ? "carousel-dot carousel-dot-active" : "carousel-dot"} key={game.id} type="button" onClick={() => onSlideChange(index)} aria-label={`Afficher ${game.titre}`} />)}
      </div>
    </section>
  )
}
