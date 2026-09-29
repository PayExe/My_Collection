import { useEffect, useState, type CSSProperties } from "react"
import { Link } from "react-router-dom"

import { useAuth } from "../hooks/useAuth"
import { ApiRequestError } from "../services/apiClient"
import { getCategories, getGames } from "../services/catalogService"
import type { Item } from "../types/api"
import "../styles/home.css"

const cubeColors = [
  ["#203d5a", "#ffbd59"],
  ["#294f43", "#d9ed72"],
  ["#493466", "#f48fb1"],
  ["#743c36", "#ff8d6b"],
  ["#304a5d", "#b1d8ef"],
  ["#674b35", "#f3c98b"],
] as const

function ArrowIcon({ direction }: { direction: "left" | "right" }) {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="icon">
      <path d={direction === "left" ? "m15 5-7 7 7 7" : "m9 5 7 7-7 7"} />
    </svg>
  )
}

function SettingsIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="icon">
      <path d="M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Z" />
      <path d="m19 13.4 1.2 1-.2 1.8-1.6.8-.3 1.8-1.6.8-1.4-.8-1.5 1.1-1.7-.6-.3-1.7-1.7-.6-1.1-1.4.6-1.7-1-1.5.6-1.7 1.7-.3.6-1.7 1.4-1 1.7.6 1.5-1.1 1.7.6.3 1.7 1.7.6 1.1 1.4-.6 1.7 1 1.5-.6 1.7-1.7.3-.6 1.7-1.4 1Z" />
    </svg>
  )
}

function UserIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="icon">
      <circle cx="12" cy="8" r="3.2" />
      <path d="M5.5 20c.7-3.4 2.9-5.2 6.5-5.2s5.8 1.8 6.5 5.2" />
    </svg>
  )
}

export function HomePage() {
  const { user, signOut } = useAuth()
  const [search, setSearch] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("Tous")
  const [activeSlide, setActiveSlide] = useState(0)
  const [games, setGames] = useState<Item[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [limit, setLimit] = useState(6)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    getCategories()
      .then((response) => setCategories(response))
      .catch(() => setCategories([]))
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setIsLoading(true)
      setError("")
      getGames({ query: search, category: selectedCategory, page, limit })
        .then((response) => {
          setGames(response.results)
          setTotal(response.total)
        })
      .catch((reason: unknown) => {
        setError(reason instanceof ApiRequestError ? reason.message : "Impossible de charger le catalogue.")
      })
      .finally(() => setIsLoading(false))
    }, search ? 400 : 0)
    return () => window.clearTimeout(timer)
  }, [limit, page, search, selectedCategory])

  const filterCategories = ["Tous", ...categories]
  const featuredGame = games[activeSlide % Math.max(games.length, 1)]

  function changeSlide(direction: "previous" | "next") {
    if (games.length === 0) return
    setActiveSlide((current) => direction === "next"
      ? (current + 1) % games.length
      : (current - 1 + games.length) % games.length)
  }

  return (
    <main className="collection-shell">
      <aside className="collection-sidebar">
        <Link className="collection-logo" to="/home" aria-label="Retour à l'accueil">
          <span className="logo-mark">GF</span>
          <span>Gamefolio</span>
        </Link>
        <nav className="sidebar-nav" aria-label="Filtres du catalogue">
          <p className="filter-title">Filtrer les jeux</p>
          {filterCategories.map((category) => (
            <button
              className={selectedCategory === category ? "sidebar-link sidebar-link-active" : "sidebar-link"}
              key={category}
              type="button"
              onClick={() => { setSelectedCategory(category); setPage(1); setActiveSlide(0) }}
            >
              {category}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <p>Affine ta recherche<br />et trouve ton prochain jeu.</p>
          <Link className="sidebar-catalog-link" to="/games">Ouvrir le catalogue</Link>
          <button className="logout-button" type="button" onClick={signOut}>Se déconnecter</button>
        </div>
      </aside>

      <section className="collection-content">
        <header className="collection-header">
          <label className="search-box">
            <span className="search-icon" aria-hidden="true">⌕</span>
            <span className="sr-only">Rechercher un jeu</span>
            <input type="search" value={search} onChange={(event) => { setSearch(event.target.value); setPage(1); setActiveSlide(0) }} placeholder="Rechercher un jeu" />
          </label>
          <div className="header-actions">
            <button className="header-icon-button" type="button" aria-label="Paramètres"><SettingsIcon /></button>
            <button className="account-button" type="button" aria-label="Compte"><UserIcon /><span>{user?.email?.split("@")[0] ?? "Compte"}</span></button>
          </div>
        </header>

        <div className="home-main">
          {isLoading && <p className="catalog-message">Chargement du catalogue...</p>}
          {error && <p className="catalog-message catalog-error">{error}</p>}
          {!isLoading && !error && games.length === 0 && <p className="catalog-message">Le catalogue est vide. Lance le seed de l'API.</p>}
          {!isLoading && !error && featuredGame && (
            <section className="featured-section" aria-label="Jeu mis en avant">
              <button className="carousel-arrow carousel-arrow-left" type="button" onClick={() => changeSlide("previous")} aria-label="Jeu précédent"><ArrowIcon direction="left" /></button>
              <div className="featured-card" style={{ backgroundColor: cubeColors[activeSlide % cubeColors.length][0] }}>
                <div className="featured-copy">
                  <p className="card-kicker">Choix du moment · {featuredGame.categorie}</p>
                  <h1>{featuredGame.titre}</h1>
                  <p>{featuredGame.description}</p>
                  <Link className="featured-link" to="/games">Découvrir le jeu <span aria-hidden="true">↗</span></Link>
                </div>
              </div>
              <button className="carousel-arrow carousel-arrow-right" type="button" onClick={() => changeSlide("next")} aria-label="Jeu suivant"><ArrowIcon direction="right" /></button>
              <div className="carousel-dots" aria-label="Sélection du jeu mis en avant">
                {games.slice(0, 4).map((game, index) => <button className={index === activeSlide ? "carousel-dot carousel-dot-active" : "carousel-dot"} key={game.id} type="button" onClick={() => setActiveSlide(index)} aria-label={`Afficher ${game.titre}`} />)}
              </div>
            </section>
          )}

          {!isLoading && !error && (
            <section className="games-section">
              <div className="section-heading"><div><p className="section-label">À explorer</p><h2>Jeux populaires</h2></div><Link to="/games">Voir tout <span aria-hidden="true">→</span></Link></div>
              <div className="game-grid">
                {games.map((game, index) => {
                  const colors = cubeColors[index % cubeColors.length]
                  return <Link className="game-card" to="/games" key={game.id}>
                    <div className="game-cover" style={{ backgroundColor: colors[0] }}>
                      <span className="game-number">{String(index + 1).padStart(2, "0")}</span>
                      <span className="game-cube" style={{ "--cube-color": colors[1] } as CSSProperties} aria-hidden="true"><span className="cube-face cube-front" /><span className="cube-face cube-top" /><span className="cube-face cube-side" /></span>
                      <strong>{game.titre}</strong>
                    </div>
                    <div className="game-card-meta"><strong>{game.titre}</strong><span>{game.categorie}</span></div>
                  </Link>
                })}
              </div>
              {games.length === 0 && total > 0 && <p className="empty-search">Aucun jeu ne correspond à ta recherche.</p>}
              {total > 0 && <div className="catalog-pagination">
                <label htmlFor="page-size">Jeux par page
                  <select id="page-size" value={limit} onChange={(event) => { setLimit(Number(event.target.value)); setPage(1) }}>
                    <option value="6">6</option>
                    <option value="12">12</option>
                    <option value="24">24</option>
                  </select>
                </label>
                <span>Page {page} / {Math.ceil(total / limit)}</span>
                <button type="button" disabled={page === 1} onClick={() => setPage((current) => current - 1)}>Précédent</button>
                <button type="button" disabled={page >= Math.ceil(total / limit)} onClick={() => setPage((current) => current + 1)}>Suivant</button>
              </div>}
            </section>
          )}
        </div>
      </section>
    </main>
  )
}
