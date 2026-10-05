import { Link, NavLink } from "react-router-dom"

import { useAuth } from "../hooks/useAuth"

interface PageShellProps {
  eyebrow: string
  title: string
  children: React.ReactNode
}

export function PageShell({ eyebrow, title, children }: PageShellProps) {
  const { user, signOut } = useAuth()

  return (
    <main className="app-shell">
      <header className="app-header">
        <Link className="app-brand" to="/home">
          <span className="app-brand-mark">GF</span>
          <span>Gamefolio</span>
        </Link>
        <nav className="app-nav" aria-label="Navigation principale">
          <NavLink to="/home">Accueil</NavLink>
          <NavLink to="/games">Catalogue</NavLink>
          <NavLink to="/collection">Ma collection</NavLink>
          <NavLink to="/stats">Statistiques</NavLink>
        </nav>
        <div className="app-account">
          {user ? <><span>{user.email}</span><button type="button" onClick={signOut}>Déconnexion</button></> : <Link to="/">Connexion</Link>}
        </div>
      </header>
      <section className="page-content">
        <p className="page-eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        {children}
      </section>
    </main>
  )
}
