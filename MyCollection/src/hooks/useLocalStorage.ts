import { useState } from "react"

export function useLocalStorage<T>(
  key: string,
  initialValue: T,
): [T, (value: T) => void] {
  const [value, setValue] = useState<T>(() => {
    const storedValue = localStorage.getItem(key)
    if (!storedValue) return initialValue

    try {
      return JSON.parse(storedValue) as T
    } catch {
      return initialValue
    }
  })

  function setStoredValue(nextValue: T): void {
    setValue(nextValue)
    localStorage.setItem(key, JSON.stringify(nextValue))
  }

  return [value, setStoredValue]
}
