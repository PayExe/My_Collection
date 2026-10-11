interface ArrowIconProps {
  direction: "left" | "right"
}

export function ArrowIcon({ direction }: ArrowIconProps) {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="icon">
      <path d={direction === "left" ? "m15 5-7 7 7 7" : "m9 5 7 7-7 7"} />
    </svg>
  )
}

export function SettingsIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="icon">
      <path d="M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Z" />
      <path d="m19 13.4 1.2 1-.2 1.8-1.6.8-.3 1.8-1.6.8-1.4-.8-1.5 1.1-1.7-.6-.3-1.7-1.7-.6-1.1-1.4.6-1.7-1-1.5.6-1.7 1.7-.3.6-1.7 1.4-1 1.7.6 1.5-1.1 1.7.6.3 1.7 1.7.6 1.1 1.4-.6 1.7 1 1.5-.6 1.7-1.7.3-.6 1.7-1.4 1Z" />
    </svg>
  )
}

export function UserIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="icon">
      <circle cx="12" cy="8" r="3.2" />
      <path d="M5.5 20c.7-3.4 2.9-5.2 6.5-5.2s5.8 1.8 6.5 5.2" />
    </svg>
  )
}
