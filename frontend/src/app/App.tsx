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
import { Contact } from '../components/Contact';
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
function Brand({ navbar = false }: { navbar?: boolean }) {
  return (
    <Link
      className={`brand${navbar ? ' brand-navbar' : ''}`}
      to="/"
      aria-label="Smolink home"
    >
      {navbar ? (
        <>
          <img
            className="brand-symbol"
            src="/smolink-symbol.png"
            alt=""
            width={592}
            height={570}
          />
          <img
            className="brand-wordmark"
            src="/smolink-wordmark.png"
            alt=""
            width={1188}
            height={287}
          />
        </>
      ) : (
        <img
          className="brand-logo"
          src="/Interlocking%20S%20Smolink%20Retro%20Logo.png"
          alt=""
          width={1448}
          height={1086}
        />
      )}
    </Link>
  );
}
function SocialLinks() {
  const [badgeFailed, setBadgeFailed] = useState(false);
  return (
    <div className="header-social">
      <a
        className="button-link button-small button-secondary github-link"
        href="https://github.com/Debrato2005/smolink"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Star Smolink on GitHub"
      >
        {badgeFailed ? (
          <span>Star</span>
        ) : (
          <img
            className="github-stars"
            src="https://img.shields.io/github/stars/Debrato2005/smolink?style=flat-square&label=&color=fffdf5"
            alt="GitHub star count"
            height={24}
            referrerPolicy="no-referrer"
            onError={() => setBadgeFailed(true)}
          />
        )}
        <Icon name="github" size={22} />
      </a>
      <a
        className="button-link button-small button-secondary x-link"
        href="https://x.com/DebratoG"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Debrato on X"
      >
        <Icon name="x" size={22} />
      </a>
    </div>
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
  const [contact, setContact] = useState(false);
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
          <Brand navbar />
          <nav className="desktop-nav" aria-label="Main navigation">
            <Link className="nav-item" to="/#how-it-works">
              How it works
            </Link>
            <Link className="nav-item" to="/#questions">
              Questions
            </Link>
            <NavLink className="nav-item" to="/dashboard">
              Workspace
            </NavLink>
            <button className="nav-item" onClick={() => setContact(true)}>
              Contact me
            </button>
          </nav>
          <div className="header-actions">
            {email ? (
              <Link
                className="button-link button-small button-ink"
                to="/dashboard"
              >
                My links
                <Icon name="arrow" size={16} />
              </Link>
            ) : (
              <>
                <NavLink
                  className="button-link button-small button-secondary sign-in-link"
                  to="/login"
                >
                  Sign in
                </NavLink>
                <Link
                  className="button-link button-small button-ink"
                  to="/register"
                >
                  Sign up
                  <Icon name="arrow" size={16} />
                </Link>
              </>
            )}
            <SocialLinks />
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
            <Link className="nav-item" to="/#how-it-works">
              How it works
            </Link>
            <Link className="nav-item" to="/#questions">
              Questions
            </Link>
            <NavLink className="nav-item" to="/dashboard">
              Workspace
            </NavLink>
            <button
              className="nav-item"
              onClick={(event) => {
                event.stopPropagation();
                setContact(true);
              }}
            >
              Contact me
            </button>
            {!email && (
              <NavLink className="nav-item" to="/login">
                Sign in
              </NavLink>
            )}
            <SocialLinks />
          </nav>
        )}
      </header>
      <Contact open={contact} onOpenChange={setContact} />
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
      <footer className="site-footer">
        <div className="container">
          <div className="footer-grid">
            <div className="footer-brand">
              <Brand />
              <div className="footer-identity">
                <a
                  className="footer-credit"
                  href="https://github.com/Debrato2005"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Icon name="github" size={18} />
                  Built by debrato
                </a>
                <p className="footer-note">
                  © {new Date().getFullYear()} Smolink.
                </p>
              </div>
            </div>
            <div className="footer-actions">
              <Button
                className="button-secondary"
                onClick={() => setContact(true)}
              >
                Contact me
              </Button>
              <a
                className="button-link footer-support"
                href="https://onlychai.neocities.org/support?name=debrato&upi=debrato2005%40oksbi"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Icon name="coffee" />
                OnlyChai
              </a>
              <Button
                className="footer-support"
                disabled
                aria-label="Ko-fi (coming soon)"
              >
                <Icon name="coffee" />
                Ko-fi
              </Button>
            </div>
          </div>
          {import.meta.env.DEV && links.source === 'fixture' && (
            <details className="demo-controls">
              <summary>
                Developer tools
                <Icon name="info" size={16} />
              </summary>
              <div>
                <label htmlFor="demo-scenario">Data scenario</label>
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
                  Reset local data
                </Button>
                <p className="field-help">
                  Local development data. Visible in development builds only.
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
