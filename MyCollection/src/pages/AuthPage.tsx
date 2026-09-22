import { useState, type FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"

import type { AuthCredentials } from "../types/api"
import { useAuth } from "../hooks/useAuth"
import { ApiRequestError } from "../services/apiClient"
import { loginUser, registerUser } from "../services/authService"
import "../styles/auth.css"

type AuthMode = "login" | "register"

interface AuthPageProps {
  mode: AuthMode
}

export function AuthPage({ mode }: AuthPageProps) {
  const navigate = useNavigate()
  const { signIn } = useAuth()
  const isRegister = mode === "register"
  const [credentials, setCredentials] = useState<AuthCredentials>({
    email: "",
    password: "",
  })
  const [confirmation, setConfirmation] = useState("")
  const [error, setError] = useState("")
  const [notice, setNotice] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  function updateField(field: keyof AuthCredentials, value: string) {
    setCredentials((current) => ({ ...current, [field]: value }))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError("")
    setNotice("")

    if (isRegister && credentials.password !== confirmation) {
      setError("Les mots de passe ne correspondent pas.")
      return
    }

    setIsSubmitting(true)
    try {
      if (isRegister) {
        await registerUser(credentials)
        navigate("/login")
      } else {
        const response = await loginUser(credentials)
        await signIn(response.access_token)
        navigate("/home")
      }
    } catch (reason: unknown) {
      setError(
        reason instanceof ApiRequestError
          ? reason.message
          : "Impossible de contacter le serveur.",
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-intro" aria-label="Présentation">
        <Link className="auth-brand" to="/">
          <span className="brand-mark">MC</span>
          <span>Ma Collection</span>
        </Link>
        <div className="intro-copy">
          <p className="eyebrow">Ludothèque personnelle</p>
          <h1>Garde une trace de chaque aventure.</h1>
          <p>
            Retrouve tes jeux, organise tes envies et construis une collection
            qui te ressemble.
          </p>
        </div>
        <p className="intro-footnote">Une collection. Tous tes mondes.</p>
      </section>

      <section className="auth-panel">
        <div className="auth-card">
          <div className="auth-heading">
            <p className="eyebrow">{isRegister ? "Nouveau membre" : "Bon retour"}</p>
            <h2>{isRegister ? "Créer un compte" : "Se connecter"}</h2>
            <p>
              {isRegister
                ? "Commence à cataloguer tes jeux en quelques secondes."
                : "Retrouve ta collection là où tu l'as laissée."}
            </p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <label htmlFor="email">Adresse email</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              value={credentials.email}
              onChange={(event) => updateField("email", event.target.value)}
              placeholder="toi@exemple.fr"
              required
            />

            <label htmlFor="password">Mot de passe</label>
            <input
              id="password"
              type="password"
              autoComplete={isRegister ? "new-password" : "current-password"}
              value={credentials.password}
              onChange={(event) => updateField("password", event.target.value)}
              placeholder="8 caractères minimum"
              minLength={8}
              required
            />

            {isRegister && (
              <>
                <label htmlFor="confirmation">Confirmer le mot de passe</label>
                <input
                  id="confirmation"
                  type="password"
                  autoComplete="new-password"
                  value={confirmation}
                  onChange={(event) => setConfirmation(event.target.value)}
                  placeholder="Répète ton mot de passe"
                  minLength={8}
                  required
                />
              </>
            )}

            {error && <p className="form-message form-error">{error}</p>}
            {notice && <p className="form-message form-success">{notice}</p>}

            <button className="auth-submit" type="submit" disabled={isSubmitting}>
              {isSubmitting
                ? "Chargement..."
                : isRegister
                  ? "Créer mon compte"
                  : "Ouvrir ma collection"}
            </button>
          </form>

          <p className="auth-switch">
            {isRegister ? "Tu as déjà un compte ?" : "Pas encore de compte ?"}{" "}
            <Link to={isRegister ? "/login" : "/register"}>
              {isRegister ? "Se connecter" : "S'inscrire"}
            </Link>
          </p>
        </div>
      </section>
    </main>
  )
}
