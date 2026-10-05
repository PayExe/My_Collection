/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"

import { PageShell } from "../components/PageShell"
import { useAuth } from "../hooks/useAuth"
import { ApiRequestError } from "../services/apiClient"
import { getGame } from "../services/catalogService"
import type { Item } from "../types/api"
import "../styles/app-pages.css"

export function GameDetailPage() {
  const { itemId } = useParams()
  const { user } = useAuth()
  const [game, setGame] = useState<Item | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    const id = Number(itemId)
    if (!Number.isInteger(id) || id <= 0) {
      setError("Jeu introuvable.")
      return
    }
    getGame(id)
      .then(setGame)
      .catch((reason: unknown) => {
        setError(reason instanceof ApiRequestError ? reason.message : "Jeu introuvable.")
      })
  }, [itemId])

  return (
    <PageShell eyebrow="Fiche jeu" title={game?.titre ?? "Détail du jeu"}>
      {error && <p className="error-state">{error}</p>}
      {!error && !game && <p className="loading-state">Chargement de la fiche...</p>}
      {game && (
        <section className="detail-grid">
          <article className="detail-card"><img src={game.image_url} alt={`Illustration de ${game.titre}`} /></article>
          <article className="detail-card detail-copy">
            <p className="section-eyebrow">{game.categorie} · {game.annee}</p>
            <h2>{game.titre}</h2>
            <p>{game.description}</p>
            <div className="item-meta"><span>{game.studio}</span><span>{game.plateforme}</span></div>
            {user ? <Link className="primary-button" to={`/game-edit?item_id=${game.id}`}>Ajouter à ma collection</Link> : <Link className="primary-button" to="/">Se connecter pour l'ajouter</Link>}
          </article>
        </section>
      )}
    </PageShell>
  )
}
