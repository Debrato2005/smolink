import { Link } from 'react-router';

export function Unavailable({
  title,
  message,
}: {
  title: string;
  message: string;
}) {
  return (
    <section className="unavailable container">
      <h1>{title}</h1>
      <p className="lead">{message}</p>
      <p>Guest link previews are available without an account.</p>
      <Link className="button-link" to="/">
        Back to short links
      </Link>
    </section>
  );
}
