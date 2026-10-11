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

export function UserIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="icon">
      <circle cx="12" cy="8" r="3.2" />
      <path d="M5.5 20c.7-3.4 2.9-5.2 6.5-5.2s5.8 1.8 6.5 5.2" />
    </svg>
  )
}
