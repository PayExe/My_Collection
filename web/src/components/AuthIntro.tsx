import { Link } from "react-router-dom"

export function AuthIntro() {
  return (
    <section className="auth-intro" aria-label="Présentation">
      <Link className="auth-brand" to="/">
        <span className="brand-mark">GF</span>
        <span>Gamefolio</span>
      </Link>
      <div className="intro-copy">
        <p className="eyebrow">Collection de jeux</p>
        <h1>Tous tes jeux, au même endroit.</h1>
        <p>
          Garde une trace de ce que tu possèdes et de ce que tu veux
          découvrir.
        </p>
        <Link className="intro-catalog-link" to="/games">
          Parcourir le catalogue sans compte →
        </Link>
      </div>
      <p className="intro-footnote">Gamefolio — ta collection de jeux.</p>
    </section>
  )
}
