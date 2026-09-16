import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <section>
      <h1>404</h1>
      <p>Cette page n'existe pas.</p>
      <Link className="button-link" to="/">
        Retour à l'accueil
      </Link>
    </section>
  );
}
