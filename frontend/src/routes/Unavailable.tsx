import { Link, useLocation } from 'react-router';
import { Icon } from '../components/ui/Icon';

export function Unavailable({
  title,
  message,
}: {
  title: string;
  message: string;
}) {
  const { pathname } = useLocation();
  return (
    <section className="unavailable container">
      {/* The missing path, drawn as a ticket stub that was cut too short. */}
      <div className="lost-ticket" aria-hidden="true">
        <span className="lost-ticket-stub">
          <Icon name="scissors" size={28} />
        </span>
        <span className="lost-ticket-body mono">{pathname}</span>
      </div>
      <h1>{title}</h1>
      <p className="lead">{message}</p>
      <p>Guest link previews are available without an account.</p>
      <Link className="button-link" to="/">
        Back to short links
        <Icon name="arrow" />
      </Link>
    </section>
  );
}
