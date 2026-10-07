import { useCallback, useRef, useState } from 'react';
import {
  BrowserRouter,
  Link,
  NavLink,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from 'react-router';
import { Home } from '../routes/Home';
import { Unavailable } from '../routes/Unavailable';
import { AuthPage } from '../features/auth/AuthPage';
import { Dashboard } from '../features/workspace/Dashboard';
import { LinkDetail } from '../features/workspace/LinkDetail';
import { Analytics } from '../features/workspace/Analytics';
import { WorkspaceLayout } from '../features/workspace/WorkspaceLayout';
import { ShortenPreview } from '../features/shorten/ShortenPreview';
import type {
  AccountAction,
  DemoScenario,
  ProductGateway,
} from '../lib/api/contracts';
import { Button } from '../components/ui/Button';
import { Icon } from '../components/ui/Icon';
import { ErrorBoundary } from './ErrorBoundary';
import { NavigationFocus } from './router/NavigationFocus';

const accountRoutes: [string, AccountAction][] = [
  ['/login', 'login'],
  ['/register', 'register'],
  ['/verify-email', 'verify-email'],
  ['/forgot-password', 'forgot-password'],
  ['/reset-password', 'reset-password'],
  ['/resend-verification', 'resend-verification'],
];
function Brand() {
  return (
    <Link className="brand" to="/" aria-label="Smolink home">
      <svg viewBox="0 0 40 40" aria-hidden="true">
        <path
          d="M4 9h23v15H4zM13 17h23v15H13z"
          fill="var(--accent-yellow)"
          stroke="var(--ink)"
          strokeWidth="3"
        />
      </svg>
      smolink<span>.</span>
    </Link>
  );
}
function Shell({
  links,
  initialToken,
}: {
  links: ProductGateway;
  initialToken: string;
}) {
  const [email, setEmail] = useState<string | null>(null);
  const [credential, setCredential] = useState(initialToken);
  const clearToken = useCallback(() => setCredential(''), []);
  const [menu, setMenu] = useState(false);
  const menuButton = useRef<HTMLButtonElement>(null);
  const [scenario, setScenario] = useState<DemoScenario>('normal');
  const [revision, setRevision] = useState(0);
  const location = useLocation();
  const navigate = useNavigate();
  const workspace = location.pathname.startsWith('/dashboard');
  function logout() {
    setEmail(null);
    links.resetDemo?.();
    setScenario('normal');
    setRevision((r) => r + 1);
    navigate('/login');
  }
  return (
    <>
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <header
        className="site-header"
        onKeyDown={(event) => {
          if (menu && event.key === 'Escape') {
            setMenu(false);
            menuButton.current?.focus();
          }
        }}
      >
        <div className="container header-inner">
          <Brand />
          <nav className="desktop-nav" aria-label="Main navigation">
            <Link to="/#features">The little things</Link>
            <Link to="/#how-it-works">How it works</Link>
            <NavLink to="/dashboard">Workspace</NavLink>
          </nav>
          <div className="header-actions">
            {email ? (
              <Link className="button-link button-small" to="/dashboard">
                My links
                <Icon name="arrow" size={16} />
              </Link>
            ) : (
              <>
                <Link className="sign-in-link" to="/login">
                  Sign in
                </Link>
                <Link className="button-link button-small" to="/register">
                  Sign up
                  <Icon name="arrow" size={16} />
                </Link>
              </>
            )}
            <button
              ref={menuButton}
              className="icon-button mobile-menu-button"
              aria-label={menu ? 'Close navigation' : 'Open navigation'}
              aria-expanded={menu}
              aria-controls="mobile-nav"
              onClick={() => setMenu(!menu)}
            >
              <Icon name={menu ? 'close' : 'menu'} />
            </button>
          </div>
        </div>
        {menu && (
          <nav
            id="mobile-nav"
            className="mobile-nav"
            aria-label="Mobile navigation"
            onClick={() => setMenu(false)}
          >
            <Link to="/#features">The little things</Link>
            <Link to="/#how-it-works">How it works</Link>
            <Link to="/dashboard">Workspace</Link>
            <Link to="/login">Sign in</Link>
          </nav>
        )}
      </header>
      <div
        className={`mode-banner ${links.source === 'live' ? 'mode-live' : ''}`}
      >
        <div className="container">
          <span>
            <span className="mode-dot" />
            {links.source === 'fixture' ? 'Demo mode' : 'Live API mode'}
          </span>
          <span>
            {links.source === 'fixture'
              ? 'Sample data. Changes reset on reload. Links do not redirect.'
              : 'Guest requests use the API. Account tools and redirects are unavailable.'}
          </span>
        </div>
      </div>
      <main
        id="main"
        tabIndex={-1}
        className={workspace ? 'page workspace-page' : 'page'}
      >
        <Routes>
          <Route path="/" element={<Home links={links} />} />
          {accountRoutes.map(([path, kind]) => (
            <Route
              key={path}
              path={path}
              element={
                <AuthPage
                  key={kind}
                  kind={kind}
                  links={links}
                  onLogin={setEmail}
                  initialToken={credential}
                  clearToken={clearToken}
                />
              }
            />
          ))}
          <Route
            path="/dashboard"
            element={
              <WorkspaceLayout email={email} links={links} onLogout={logout} />
            }
          >
            <Route
              index
              element={<Dashboard links={links} revision={revision} />}
            />
            <Route
              path="new"
              element={
                <div className="workspace-create">
                  <Link className="back-link" to="/dashboard">
                    <Icon name="back" />
                    All links
                  </Link>
                  <h1>Create a link</h1>
                  <p className="muted">One more thing worth sharing.</p>
                  <ShortenPreview links={links} />
                  <Link className="text-link" to="/dashboard">
                    Back to all links
                    <Icon name="arrow" />
                  </Link>
                </div>
              }
            />
            <Route
              path="urls/:id"
              element={
                <LinkDetail
                  key={location.pathname}
                  links={links}
                  revision={revision}
                />
              }
            />
            <Route
              path="urls/:id/analytics"
              element={
                <Analytics
                  key={location.pathname}
                  links={links}
                  revision={revision}
                />
              }
            />
          </Route>
          <Route
            path="*"
            element={
              <Unavailable
                title="Page not found"
                message="This link took a little detour. Let us get you back."
              />
            }
          />
        </Routes>
      </main>
      <NavigationFocus />
      <footer className={`site-footer ${workspace ? 'footer-compact' : ''}`}>
        <div className="container">
          <div className="footer-top">
            <div>
              <Brand />
              <p>Less link. More possibility.</p>
            </div>
            <nav aria-label="Footer navigation">
              <Link to="/#features">Features</Link>
              <Link to="/#questions">Questions</Link>
              <Link to="/dashboard">Workspace</Link>
            </nav>
            <span className="footer-stamp">
              A little link
              <br />
              goes a long way.
              <Icon name="arrow" size={28} />
            </span>
          </div>
          <div className="footer-bottom">
            <span>© {new Date().getFullYear()} Smolink</span>
            <span>Made for things worth sharing.</span>
            <a href="/#shorten">Back to the little things ↑</a>
          </div>
          {links.source === 'fixture' && (
            <details className="demo-controls">
              <summary>
                Demo controls
                <Icon name="info" size={16} />
              </summary>
              <div>
                <label htmlFor="demo-scenario">Preview a state</label>
                <select
                  id="demo-scenario"
                  value={scenario}
                  onChange={(e) => {
                    const next = e.target.value as DemoScenario;
                    setScenario(next);
                    links.setScenario?.(next);
                    setRevision((r) => r + 1);
                  }}
                >
                  <option value="normal">Normal</option>
                  <option value="empty">Empty workspace</option>
                  <option value="error">Service unavailable</option>
                  <option value="limited">Rate limited</option>
                  <option value="locked">Account locked</option>
                  <option value="unverified">Email unverified</option>
                  <option value="expired">Session expired</option>
                </select>
                <Button
                  className="button-secondary button-small"
                  onClick={() => {
                    links.resetDemo?.();
                    setScenario('normal');
                    setRevision((r) => r + 1);
                  }}
                >
                  Reset demo data
                </Button>
                <p className="field-help">
                  Development fixtures only. No requests reach the API.
                </p>
              </div>
            </details>
          )}
        </div>
      </footer>
    </>
  );
}
export function App({
  links,
  initialToken = '',
}: {
  links: ProductGateway;
  initialToken?: string;
}) {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Shell links={links} initialToken={initialToken} />
      </BrowserRouter>
    </ErrorBoundary>
  );
}
