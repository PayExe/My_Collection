import { createContext } from "react"

export interface ThemeContextValue {
  isLightMode: boolean
  toggleTheme: () => void
}

export const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)
