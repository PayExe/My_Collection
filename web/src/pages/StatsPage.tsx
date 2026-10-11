import { useEffect, useState } from "react"

import { PageShell } from "../components/PageShell"
import { ApiRequestError } from "../services/apiClient"
import { getCollectionStats } from "../services/collectionService"
import type { CollectionStats } from "../types/api"
import "../styles/app-pages.css"

export function StatsPage() {
  const [stats, setStats] = useState<CollectionStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    getCollectionStats()
      .then(setStats)
      .catch((reason: unknown) => {
        setError(
          reason instanceof ApiRequestError
            ? reason.message
            : "Impossible de charger les statistiques.",
        )
      })
      .finally(() => setIsLoading(false))
  }, [])

  return (
    <PageShell eyebrow="Vue d'ensemble" title="Tes statistiques">
      {isLoading && <p className="loading-state">Calcul des statistiques...</p>}
      {error && <p className="error-state">{error}</p>}
      {!isLoading && !error && stats && (
        <section className="stats-grid" aria-label="Statistiques de collection">
          <article className="stat-card"><p className="section-eyebrow">Total</p><h2>{stats.total}</h2><p>jeux dans ta collection</p></article>
          <article className="stat-card"><p className="section-eyebrow">Note moyenne</p><h2>{stats.note_moyenne.toFixed(1)}/5</h2><p>sur l'ensemble de tes jeux notés</p></article>
          <article className="stat-card"><p className="section-eyebrow">À découvrir</p><h2>{stats.par_statut.a_decouvrir}</h2><p>prochaines aventures</p></article>
          <article className="stat-card"><p className="section-eyebrow">En cours</p><h2>{stats.par_statut.en_cours}</h2><p>jeux actuellement lancés</p></article>
          <article className="stat-card"><p className="section-eyebrow">Terminés</p><h2>{stats.par_statut.termine}</h2><p>aventures terminées</p></article>
        </section>
      )}
    </PageShell>
  )
}
