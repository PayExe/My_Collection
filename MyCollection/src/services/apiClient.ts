import type { ApiError } from "../types/api"

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

export class ApiRequestError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = "ApiRequestError"
    this.status = status
  }
}

function isApiError(value: unknown): value is ApiError {
  if (typeof value !== "object" || value === null || !("erreur" in value)) {
    return false
  }

  const error = value.erreur
  return (
    typeof error === "object" &&
    error !== null &&
    "message" in error &&
    typeof error.message === "string"
  )
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = localStorage.getItem("access_token")
  const headers = new Headers(options.headers)
  headers.set("Content-Type", "application/json")

  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  })
  const body: unknown = await response.json().catch(() => null)

  if (!response.ok) {
    const message = isApiError(body)
      ? body.erreur.message
      : "Une erreur est survenue."
    throw new ApiRequestError(message, response.status)
  }

  return body as T
}
