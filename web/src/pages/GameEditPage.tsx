/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useState } from "react"
import { useNavigate, useParams, useSearchParams } from "react-router-dom"

import { PageShell } from "../components/PageShell"
import { useCollection } from "../hooks/useCollection"
import { ApiRequestError } from "../services/apiClient"
import { getGames } from "../services/catalogService"
import type { Item, Statut } from "../types/api"
import "../styles/app-pages.css"

export function GameEditPage() {
  const navigate = useNavigate()
  const { entryId } = useParams()
  const [searchParams] = useSearchParams()
  const { entries, addEntry, updateEntry } = useCollection()
  const currentEntry = entries.find((entry) => entry.id === Number(entryId))
  const [games, setGames] = useState<Item[]>([])
  const [itemId, setItemId] = useState(Number(searchParams.get("item_id")) || 0)
  const [statut, setStatut] = useState<Statut>("a_decouvrir")
  const [note, setNote] = useState("1")
  const [commentaire, setCommentaire] = useState("")
  const [error, setError] = useState("")
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    getGames({ limit: 50 }).then((response) => setGames(response.results)).catch(() => setError("Impossible de charger les jeux."))
  }, [])

  useEffect(() => {
    if (!currentEntry) return
    setItemId(currentEntry.item.id)
    setStatut(currentEntry.statut)
    setNote(String(currentEntry.note))
    setCommentaire(currentEntry.commentaire ?? "")
  }, [currentEntry])

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    setError("")
    setIsSaving(true)
    try {
      const parsedNote = Number(note)
      if (!itemId || parsedNote < 1 || parsedNote > 5) {
        setError("Sélectionne un jeu et une note entre 1 et 5.")
        return
      }
      if (currentEntry) {
        await updateEntry(currentEntry.id, { statut, note: parsedNote, commentaire: commentaire || null })
      } else {
        await addEntry({ item_id: itemId, statut, note: parsedNote, commentaire: commentaire || null })
      }
      navigate("/collection")
    } catch (reason: unknown) {
      setError(reason instanceof ApiRequestError ? reason.message : "Impossible d'enregistrer cette entrée.")
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <PageShell eyebrow="Collection personnelle" title={currentEntry ? "Modifier l'entrée" : "Ajouter un jeu"}>
      <section className="form-card">
        <form onSubmit={handleSubmit}>
          <label htmlFor="game">Jeu</label>
          <select id="game" value={itemId} disabled={Boolean(currentEntry)} onChange={(event) => setItemId(Number(event.target.value))}>
            <option value={0}>Choisir un jeu</option>
            {games.map((game) => <option key={game.id} value={game.id}>{game.titre}</option>)}
          </select>
          <label htmlFor="status">Statut</label>
          <select id="status" value={statut} onChange={(event) => setStatut(event.target.value as Statut)}>
            <option value="a_decouvrir">À découvrir</option>
            <option value="en_cours">En cours</option>
            <option value="termine">Terminé</option>
          </select>
          <label htmlFor="note">Note</label>
          <input id="note" type="number" min="1" max="5" value={note} onChange={(event) => setNote(event.target.value)} />
          <label htmlFor="comment">Commentaire</label>
          <textarea id="comment" value={commentaire} onChange={(event) => setCommentaire(event.target.value)} placeholder="Ton avis sur ce jeu..." />
          {error && <p className="error-state">{error}</p>}
          <div className="form-actions"><button className="primary-button" type="submit" disabled={isSaving}>{isSaving ? "Enregistrement..." : "Enregistrer"}</button><button className="secondary-button" type="button" onClick={() => navigate(-1)}>Annuler</button></div>
        </form>
      </section>
    </PageShell>
  )
}
