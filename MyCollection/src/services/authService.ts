import type {
  AuthCredentials,
  AuthResponse,
  User,
} from "../types/api"
import { apiRequest } from "./apiClient"

export function registerUser(credentials: AuthCredentials): Promise<User> {
  return apiRequest<User>("/auth/register", {
    method: "POST",
    body: JSON.stringify(credentials),
  })
}

export function loginUser(credentials: AuthCredentials): Promise<AuthResponse> {
  return apiRequest<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  })
}
