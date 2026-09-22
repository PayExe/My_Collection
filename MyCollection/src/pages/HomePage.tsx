import { Link } from "react-router-dom"

export function HomePage() {
  return (
    <main className="home-page">
      <p className="eyebrow">Ma Collection</p>
      <h1>Bienvenue dans ta ludothèque.</h1>
      <p>
        Organise tes jeux vidéo, retrouve tes envies et garde une trace de tes
        prochaines aventures.
      </p>
      <div className="home-actions">
        <Link className="home-button" to="/games">
          Voir le catalogue
        </Link>
        <Link className="home-link" to="/game-edit">
          Ajouter un jeu
        </Link>
      </div>
    </main>
  )
}
