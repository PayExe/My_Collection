import { useContext } from "react"

import {
  CollectionContext,
  type CollectionContextValue,
} from "../contexts/collection-context"

export function useCollection(): CollectionContextValue {
  const context = useContext(CollectionContext)
  if (!context) {
    throw new Error("useCollection doit être utilisé dans CollectionProvider")
  }
  return context
}
