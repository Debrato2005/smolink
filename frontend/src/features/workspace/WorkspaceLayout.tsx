import { Link, Outlet, useLocation } from 'react-router';
import { useState } from 'react';
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
  const [collapsed, setCollapsed] = useState(false);
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
    <div className="workspace" data-collapsed={collapsed || undefined}>
      <aside className="workspace-sidebar">
        <div className="sidebar-heading">
          <Link to="/" className="sidebar-brand" aria-label="Smolink home">
            <img src="/smolink-symbol.png" alt="" width={38} height={38} />
            <span>smolink</span>
          </Link>
          <button
            className="icon-button sidebar-toggle"
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            aria-expanded={!collapsed}
            aria-controls="workspace-navigation"
            onClick={() => setCollapsed(!collapsed)}
          >
            <Icon name="menu" size={18} />
          </button>
        </div>
        <div className="workspace-identity">
          <span className="avatar" aria-hidden="true">
            {email.slice(0, 1).toUpperCase()}
          </span>
          <div>
            <strong>My workspace</strong>
            <span>Personal</span>
          </div>
        </div>
        <nav id="workspace-navigation" aria-label="Workspace navigation">
          <span className="sidebar-group-label">Your workspace</span>
          <Link
            to="/dashboard"
            aria-label="All links"
            aria-current={!creating && !analytics ? 'page' : undefined}
          >
            <Icon name="link" />
            <span>All links</span>
          </Link>
          <Link
            to="/dashboard?view=analytics"
            aria-label="Overview"
            aria-current={analytics ? 'page' : undefined}
          >
            <Icon name="chart" />
            <span>Overview</span>
          </Link>
          <Link
            to="/dashboard/new"
            aria-label="Create a link"
            aria-current={creating ? 'page' : undefined}
          >
            <Icon name="plus" />
            <span>Create a link</span>
          </Link>
        </nav>
        <div className="workspace-user">
          <span className="small muted break-word">{email}</span>
          <Button
            className="button-plain"
            onClick={onLogout}
            aria-label="Sign out"
          >
            <Icon name="logout" />
            <span>Sign out</span>
          </Button>
        </div>
      </aside>
      <div className="workspace-content">
        <Outlet />
      </div>
    </div>
  );
}
