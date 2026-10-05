import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { PageShell } from "../components/PageShell"
import { ApiRequestError } from "../services/apiClient"
import { getCategories, getGames } from "../services/catalogService"
import type { Item } from "../types/api"
import "../styles/app-pages.css"
import "../styles/catalog.css"

export function GamePage() {
  const [games, setGames] = useState<Item[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [query, setQuery] = useState("")
  const [category, setCategory] = useState("")
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    getCategories().then(setCategories).catch(() => setCategories([]))
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setIsLoading(true)
      setError("")
      getGames({ query, category, limit: 12, page })
        .then((response) => {
          setGames(response.results)
          setTotal(response.total)
        })
        .catch((reason: unknown) => {
          setError(
            reason instanceof ApiRequestError
              ? reason.message
              : "Impossible de charger le catalogue.",
          )
        })
        .finally(() => setIsLoading(false))
    }, query ? 400 : 0)
    return () => window.clearTimeout(timer)
  }, [category, page, query])

  const totalPages = Math.max(1, Math.ceil(total / 12))

  return (
    <PageShell eyebrow="Catalogue public" title="Explorer les jeux">
      <div className="page-toolbar">
        <input
          type="search"
          value={query}
          placeholder="Rechercher un jeu..."
          onChange={(event) => { setQuery(event.target.value); setPage(1) }}
        />
        <select value={category} onChange={(event) => { setCategory(event.target.value); setPage(1) }}>
          <option value="">Toutes les catégories</option>
          {categories.map((itemCategory) => <option key={itemCategory} value={itemCategory}>{itemCategory}</option>)}
        </select>
      </div>

      {isLoading && <p className="loading-state">Chargement du catalogue...</p>}
      {error && <p className="error-state">{error}</p>}
      {!isLoading && !error && games.length === 0 && <p className="empty-state">Aucun jeu ne correspond à ta recherche.</p>}
      {!isLoading && !error && games.length > 0 && (
        <section className="catalog-grid" aria-label="Catalogue des jeux">
          {games.map((game) => (
            <Link className="catalog-card" to={`/games/${game.id}`} key={game.id}>
              <div className="catalog-cover"><span>{String(game.annee)}</span><strong>{game.titre}</strong></div>
              <div><h2>{game.titre}</h2><p>{game.categorie} · {game.plateforme}</p></div>
            </Link>
          ))}
        </section>
      )}
      {total > 0 && <div className="pagination-row"><button className="secondary-button" type="button" disabled={page === 1} onClick={() => setPage((current) => current - 1)}>Précédent</button><span>Page {page} / {totalPages}</span><button className="secondary-button" type="button" disabled={page >= totalPages} onClick={() => setPage((current) => current + 1)}>Suivant</button></div>}
    </PageShell>
  )
}
