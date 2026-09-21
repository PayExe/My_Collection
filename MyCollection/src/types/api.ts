export interface Item {
  id: number
  titre: string
  categorie: string
  description: string
  image_url: string
  annee: number
  studio: string
  plateforme: string
}

export type Statut = "a_decouvrir" | "en_cours" | "termine"

export interface Entry {
  id: number
  statut: Statut
  note: number
  commentaire: string | null
  date_ajout: string
  item: Item
}

export interface PaginatedItems {
  total: number
  page: number
  limit: number
  results: Item[]
}

export interface User {
  id: number
  email: string
}

export interface AuthResponse {
  access_token: string
  token_type: "bearer"
}

export interface AuthCredentials {
  email: string
  password: string
}

export interface ApiError {
  erreur: {
    code: number
    message: string
  }
}
