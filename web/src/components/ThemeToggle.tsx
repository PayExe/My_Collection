import { useTheme } from "../hooks/useTheme"

interface ThemeToggleProps {
  className?: string
}

export function ThemeToggle({ className }: ThemeToggleProps) {
  const { isLightMode, toggleTheme } = useTheme()

  return (
    <button className={className} type="button" onClick={toggleTheme} aria-label="Changer le thème">
      {isLightMode ? "☾ Sombre" : "☀ Clair"}
    </button>
  )
}
