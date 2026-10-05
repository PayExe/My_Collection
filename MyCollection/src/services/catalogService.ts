import { apiRequest } from "./apiClient"
import type { Item, PaginatedItems } from "../types/api"

interface CatalogQuery {
  query?: string
  category?: string
  limit?: number
  page?: number
}

export function getGames({ query = "", category = "", limit = 6, page = 1 }: CatalogQuery = {}): Promise<PaginatedItems> {
  const params = new URLSearchParams({ page: String(page), limit: String(limit) })
  if (query.trim().length >= 2) params.set("q", query.trim())
  if (category && category !== "Tous") params.set("categorie", category)
  return apiRequest<PaginatedItems>(`/items?${params.toString()}`)
}

export function getCategories(): Promise<string[]> {
  return apiRequest<string[]>("/items/categories")
}

export function getGame(itemId: number): Promise<Item> {
  return apiRequest<Item>(`/items/${itemId}`)
}
