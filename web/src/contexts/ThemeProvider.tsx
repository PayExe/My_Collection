import type { ReactNode } from "react"

import { useLocalStorage } from "../hooks/useLocalStorage"
import { ThemeContext } from "./theme-context"

interface ThemeProviderProps {
  children: ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [isLightMode, setIsLightMode] = useLocalStorage("gamefolio-light-mode", false)

  function toggleTheme(): void {
    setIsLightMode(!isLightMode)
  }

  return (
    <ThemeContext.Provider value={{ isLightMode, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}
