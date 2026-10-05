import type {
  CollectionCreate,
  CollectionStats,
  CollectionUpdate,
  Entry,
  Statut,
} from "../types/api"
import { apiRequest } from "./apiClient"

export interface CollectionQuery {
  statut?: Statut
  tri?: "date" | "note"
}

export function getCollection(query: CollectionQuery = {}): Promise<Entry[]> {
  const params = new URLSearchParams()
  if (query.statut) params.set("statut", query.statut)
  if (query.tri) params.set("tri", query.tri)
  const suffix = params.toString() ? `?${params.toString()}` : ""
  return apiRequest<Entry[]>(`/me/collection${suffix}`)
}

export function addToCollection(payload: CollectionCreate): Promise<Entry> {
  return apiRequest<Entry>("/me/collection", {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

export function updateCollectionEntry(
  entryId: number,
  payload: CollectionUpdate,
): Promise<Entry> {
  return apiRequest<Entry>(`/me/collection/${entryId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  })
}

export async function deleteCollectionEntry(entryId: number): Promise<void> {
  await apiRequest<null>(`/me/collection/${entryId}`, {
    method: "DELETE",
  })
}

export function getCollectionStats(): Promise<CollectionStats> {
  return apiRequest<CollectionStats>("/me/stats")
}
