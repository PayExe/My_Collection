import { useCallback, useEffect, useState, type ReactNode } from "react"

import { useAuth } from "../hooks/useAuth"
import { ApiRequestError } from "../services/apiClient"
import {
  addToCollection,
  deleteCollectionEntry,
  getCollection,
  updateCollectionEntry,
} from "../services/collectionService"
import type {
  CollectionCreate,
  CollectionUpdate,
  Entry,
} from "../types/api"
import { CollectionContext } from "./collection-context"

interface CollectionProviderProps {
  children: ReactNode
}

export function CollectionProvider({ children }: CollectionProviderProps) {
  const { user } = useAuth()
  const [entries, setEntries] = useState<Entry[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  const refresh = useCallback(async (): Promise<void> => {
    if (!user) {
      setEntries([])
      return
    }

    setIsLoading(true)
    setError("")
    try {
      setEntries(await getCollection({ tri: "date" }))
    } catch (reason: unknown) {
      setError(
        reason instanceof ApiRequestError
          ? reason.message
          : "Impossible de charger la collection.",
      )
    } finally {
      setIsLoading(false)
    }
  }, [user])

  useEffect(() => {
    // Loading the authenticated collection synchronizes React with the API session.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refresh()
  }, [refresh])

  async function addEntry(payload: CollectionCreate): Promise<Entry> {
    const entry = await addToCollection(payload)
    setEntries((current) => [entry, ...current])
    return entry
  }

  async function updateEntry(
    entryId: number,
    payload: CollectionUpdate,
  ): Promise<Entry> {
    const updatedEntry = await updateCollectionEntry(entryId, payload)
    setEntries((current) =>
      current.map((entry) => (entry.id === entryId ? updatedEntry : entry)),
    )
    return updatedEntry
  }

  async function removeEntry(entryId: number): Promise<void> {
    await deleteCollectionEntry(entryId)
    setEntries((current) => current.filter((entry) => entry.id !== entryId))
  }

  return (
    <CollectionContext.Provider
      value={{
        entries,
        isLoading,
        error,
        refresh,
        addEntry,
        updateEntry,
        removeEntry,
      }}
    >
      {children}
    </CollectionContext.Provider>
  )
}
