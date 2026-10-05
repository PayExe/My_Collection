import { createContext } from "react"

import type {
  CollectionCreate,
  CollectionUpdate,
  Entry,
} from "../types/api"

export interface CollectionContextValue {
  entries: Entry[]
  isLoading: boolean
  error: string
  refresh: () => Promise<void>
  addEntry: (payload: CollectionCreate) => Promise<Entry>
  updateEntry: (entryId: number, payload: CollectionUpdate) => Promise<Entry>
  removeEntry: (entryId: number) => Promise<void>
}

export const CollectionContext = createContext<
  CollectionContextValue | undefined
>(undefined)
