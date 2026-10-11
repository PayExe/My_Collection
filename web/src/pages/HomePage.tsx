import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { FeaturedCarousel } from "../components/home/FeaturedCarousel"
import { GameGrid } from "../components/home/GameGrid"
import { SettingsIcon, UserIcon } from "../components/home/HomeIcons"
import { useAuth } from "../hooks/useAuth"
import { useTheme } from "../hooks/useTheme"
import { ApiRequestError } from "../services/apiClient"
import { getCategories, getGames } from "../services/catalogService"
import type { Item } from "../types/api"
import "../styles/home.css"

export function HomePage() {
  const { user, signOut } = useAuth()
  const [search, setSearch] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("Tous")
  const [activeSlide, setActiveSlide] = useState(0)
  const [games, setGames] = useState<Item[]>([])
  const [featuredGames, setFeaturedGames] = useState<Item[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [limit, setLimit] = useState(6)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  const { isLightMode, toggleTheme } = useTheme()

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
          if (page === 1) setFeaturedGames(response.results)
        })
      .catch((reason: unknown) => {
        setError(reason instanceof ApiRequestError ? reason.message : "Impossible de charger le catalogue.")
      })
      .finally(() => setIsLoading(false))
    }, search ? 400 : 0)
    return () => window.clearTimeout(timer)
  }, [limit, page, search, selectedCategory])

  const filterCategories = ["Tous", ...categories]
  const isFiltering = search.trim().length >= 2 || selectedCategory !== "Tous"

  return (
    <main className={isLightMode ? "collection-shell light-mode" : "collection-shell"}>
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
          <Link className="sidebar-catalog-link" to="/collection">Ma collection</Link>
          <Link className="sidebar-catalog-link" to="/stats">Statistiques</Link>
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
            <button className="header-icon-button" type="button" aria-label="Changer le thème" onClick={toggleTheme}><SettingsIcon /></button>
            <Link className="account-button" to="/collection" aria-label="Ma collection"><UserIcon /><span>{user?.email?.split("@")[0] ?? "Compte"}</span></Link>
          </div>
        </header>

        <div className="home-main">
          {isLoading && <p className="catalog-message">Chargement du catalogue...</p>}
          {error && <p className="catalog-message catalog-error">{error}</p>}
          {!isLoading && !error && games.length === 0 && !isFiltering && <p className="catalog-message">Le catalogue est vide. Lance le seed de l'API.</p>}
          {!isLoading && !error && !search.trim() && (
            <FeaturedCarousel games={featuredGames} activeSlide={activeSlide} onSlideChange={setActiveSlide} />
          )}

          {!isLoading && !error && (
            <section className="games-section">
              <div className="section-heading"><div><p className="section-label">À explorer</p><h2>Jeux populaires</h2></div><Link to="/games">Voir tout <span aria-hidden="true">→</span></Link></div>
              <GameGrid games={games} />
              {games.length === 0 && isFiltering && <p className="empty-search">Aucun jeu ne correspond à ta recherche.</p>}
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
