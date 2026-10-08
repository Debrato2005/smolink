import { Link, Outlet, useLocation } from 'react-router';
import { Button } from '../../components/ui/Button';
import { Icon } from '../../components/ui/Icon';
import type { ProductGateway } from '../../lib/api/contracts';
export function WorkspaceLayout({
  email,
  links,
  onLogout,
}: {
  email: string | null;
  links: ProductGateway;
  onLogout: () => void;
}) {
  const location = useLocation();
  const creating = location.pathname === '/dashboard/new';
  const analytics =
    location.pathname.endsWith('/analytics') ||
    new URLSearchParams(location.search).get('view') === 'analytics';
  if (links.source === 'live')
    return (
      <section className="unavailable container">
        <Icon name="link" size={48} />
        <h1>Your workspace is on its way.</h1>
        <p>
          Link management and click stats are coming soon. You can shorten links
          without an account today.
        </p>
        <Link className="button-link" to="/">
          Shorten a link
          <Icon name="arrow" />
        </Link>
      </section>
    );
  if (!email)
    return (
      <section className="unavailable container">
        <Icon name="link" size={48} />
        <h1>A home for your links.</h1>
        <p>Sign in to manage your links and see who clicks them.</p>
        <Link
          className="button-link"
          to={`/login?next=${encodeURIComponent(location.pathname + location.search)}`}
        >
          Sign in
          <Icon name="arrow" />
        </Link>
      </section>
    );
  return (
    <div className="workspace">
      <aside className="workspace-sidebar">
        <div className="workspace-identity">
          <span className="avatar" aria-hidden="true">
            {email.slice(0, 1).toUpperCase()}
          </span>
          <div>
            <strong>My workspace</strong>
            <span>Personal</span>
          </div>
        </div>
        <nav aria-label="Workspace navigation">
          <Link
            to="/dashboard"
            aria-current={!creating && !analytics ? 'page' : undefined}
          >
            <Icon name="link" />
            All links
          </Link>
          <Link
            to="/dashboard?view=analytics"
            aria-current={analytics ? 'page' : undefined}
          >
            <Icon name="chart" />
            Overview
          </Link>
          <Link
            to="/dashboard/new"
            aria-current={creating ? 'page' : undefined}
          >
            <Icon name="plus" />
            Create a link
          </Link>
        </nav>
        <div className="workspace-user">
          <span className="small muted break-word">{email}</span>
          <Button className="button-plain" onClick={onLogout}>
            <Icon name="logout" />
            Sign out
          </Button>
        </div>
      </aside>
      <div className="workspace-content">
        <Outlet />
      </div>
    </div>
  );
}
