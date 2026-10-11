import { useMemo, useState } from "react"
import { Link } from "react-router-dom"

import { PageShell } from "../components/PageShell"
import { useCollection } from "../hooks/useCollection"
import { ApiRequestError } from "../services/apiClient"
import type { Statut } from "../types/api"
import "../styles/app-pages.css"

const statusLabels: Record<Statut, string> = {
  a_decouvrir: "À découvrir",
  en_cours: "En cours",
  termine: "Terminé",
}

export function CollectionPage() {
  const { entries, isLoading, error, removeEntry } = useCollection()
  const [status, setStatus] = useState<Statut | "">("")
  const [sort, setSort] = useState<"date" | "note">("date")
  const [actionError, setActionError] = useState("")

  const visibleEntries = useMemo(() => {
    const filtered = status
      ? entries.filter((entry) => entry.statut === status)
      : [...entries]
    return filtered.sort((left, right) =>
      sort === "note"
        ? right.note - left.note
        : right.date_ajout.localeCompare(left.date_ajout),
    )
  }, [entries, sort, status])

  async function handleDelete(entryId: number): Promise<void> {
    if (!window.confirm("Supprimer cette entrée de ta collection ?")) return
    setActionError("")
    try {
      await removeEntry(entryId)
    } catch (reason: unknown) {
      setActionError(
        reason instanceof ApiRequestError
          ? reason.message
          : "Impossible de supprimer cette entrée.",
      )
    }
  }

  return (
    <PageShell eyebrow="Espace personnel" title="Ma collection">
      <div className="page-toolbar">
        <select
          aria-label="Filtrer par statut"
          value={status}
          onChange={(event) => setStatus(event.target.value as Statut | "")}
        >
          <option value="">Tous les statuts</option>
          <option value="a_decouvrir">À découvrir</option>
          <option value="en_cours">En cours</option>
          <option value="termine">Terminé</option>
        </select>
        <select
          aria-label="Trier la collection"
          value={sort}
          onChange={(event) => setSort(event.target.value as "date" | "note")}
        >
          <option value="date">Plus récents</option>
          <option value="note">Meilleures notes</option>
        </select>
        <Link className="primary-button" to="/game-edit">Ajouter un jeu</Link>
      </div>

      {(error || actionError) && <p className="error-state">{error || actionError}</p>}
      {isLoading && <p className="loading-state">Chargement de ta collection...</p>}
      {!isLoading && !error && visibleEntries.length === 0 && (
        <p className="empty-state">Ta collection est vide pour ce filtre.</p>
      )}
      {!isLoading && !error && visibleEntries.length > 0 && (
        <section className="collection-list" aria-label="Entrées de collection">
          {visibleEntries.map((entry) => (
            <article className="collection-item" key={entry.id}>
              <p className="section-eyebrow">{entry.item.categorie}</p>
              <h2>{entry.item.titre}</h2>
              <p>{entry.item.studio} · {entry.item.plateforme}</p>
              <div className="item-meta">
                <span className="status-pill">{statusLabels[entry.statut]}</span>
                <span>{entry.note}/5</span>
              </div>
              {entry.commentaire && <p>“{entry.commentaire}”</p>}
              <div className="item-actions">
                <Link className="secondary-button" to={`/game-edit/${entry.id}`}>Modifier</Link>
                <button className="danger-button" type="button" onClick={() => void handleDelete(entry.id)}>Supprimer</button>
              </div>
            </article>
          ))}
        </section>
      )}
    </PageShell>
  )
}
