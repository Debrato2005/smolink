import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router';
import type { AccountAction, ProductGateway } from '../../lib/api/contracts';
import { ApiError } from '../../lib/api/errors';
import { safeReturn } from '../../lib/validation';
import { Button } from '../../components/ui/Button';
import { Field } from '../../components/ui/Field';
import { Icon } from '../../components/ui/Icon';
import { ErrorNotice } from '../../components/ui/Feedback';

const content: Record<
  AccountAction,
  { title: string; description: string; action: string }
> = {
  login: {
    title: 'Sign in',
    description: 'Your little corner of the internet awaits.',
    action: 'Sign in',
  },
  register: {
    title: 'Create an account',
    description: 'A home for every link worth keeping.',
    action: 'Create account',
  },
  'verify-email': {
    title: 'Verify your email',
    description: 'One small step before your first big share.',
    action: 'Verify email',
  },
  'forgot-password': {
    title: 'Recover your account',
    description: 'It happens. Let us help you find your way back.',
    action: 'Send reset link',
  },
  'reset-password': {
    title: 'Choose a new password',
    description: 'A fresh start for your account.',
    action: 'Reset password',
  },
  'resend-verification': {
    title: 'Request a new email',
    description: 'Get a new link to verify your email address.',
    action: 'Send verification link',
  },
};
export function AuthPage({
  kind,
  links,
  onLogin,
  initialToken,
  clearToken,
}: {
  kind: AccountAction;
  links: ProductGateway;
  onLogin: (email: string) => void;
  initialToken: string;
  clearToken: () => void;
}) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [show, setShow] = useState(false);
  const [token, setToken] = useState(initialToken);
  const [fields, setFields] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [done, setDone] = useState(false);
  const pending = useRef<AbortController | null>(null);
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const fixture = links.source === 'fixture';
  const needEmail = [
    'login',
    'register',
    'forgot-password',
    'resend-verification',
  ].includes(kind);
  const needPassword = ['login', 'register', 'reset-password'].includes(kind);
  const needToken = ['verify-email', 'reset-password'].includes(kind);
  const copy = content[kind];
  useEffect(
    () => () => {
      pending.current?.abort();
      clearToken();
    },
    [clearToken],
  );
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending.current) return;
    const errors: Record<string, string> = {};
    if (needEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim()))
      errors.email = 'Enter a valid email address.';
    if (
      needPassword &&
      (Array.from(password).length < 12 || Array.from(password).length > 128)
    )
      errors.password = 'Use 12–128 characters for your password.';
    setFields(errors);
    setError(null);
    if (Object.keys(errors).length) {
      event.currentTarget
        .querySelector<HTMLInputElement>(`[name="${Object.keys(errors)[0]}"]`)
        ?.focus();
      return;
    }
    const controller = new AbortController();
    pending.current = controller;
    setBusy(true);
    try {
      await links.account(
        kind,
        { email: email.trim().toLowerCase(), password, token },
        controller.signal,
      );
      if (controller.signal.aborted) return;
      setPassword('');
      setToken('');
      clearToken();
      if (kind === 'login') {
        onLogin(email.trim());
        navigate(safeReturn(params.get('next')), { replace: true });
      } else setDone(true);
    } catch (e) {
      if (!controller.signal.aborted) setError(e);
    } finally {
      if (pending.current === controller) {
        pending.current = null;
        setBusy(false);
      }
    }
  }
  return (
    <section className="auth-layout container">
      <aside className="auth-poster">
        <div className="poster-top">
          <Icon name="link" size={34} />
          <span>Small by design.</span>
        </div>
        <h2>
          Less link.
          <br />
          More you.
        </h2>
        <div className="poster-geometry" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>
        <p>
          Ideas, projects, playlists.
          <br />
          Keep your world connected.
        </p>
      </aside>
      <div className="auth-content">
        <Link to="/" className="back-link">
          <Icon name="back" size={17} />
          Back to Smolink
        </Link>
        <h1>
          {done
            ? kind === 'register' ||
              kind === 'forgot-password' ||
              kind === 'resend-verification'
              ? 'Check your inbox'
              : kind === 'verify-email'
                ? 'Email verified'
                : 'Password reset'
            : copy.title}
        </h1>
        {done ? (
          <div className="auth-success">
            <span className="success-mark">
              <Icon
                name={
                  kind === 'register' ||
                  kind === 'forgot-password' ||
                  kind === 'resend-verification'
                    ? 'mail'
                    : 'check'
                }
                size={30}
              />
            </span>
            <p role="status">
              {kind === 'register'
                ? 'Demo registration complete. No account was created or email sent.'
                : kind === 'forgot-password' || kind === 'resend-verification'
                  ? 'Demo request accepted. In live service, eligible accounts receive an email. Delivery is not guaranteed.'
                  : 'Demo complete. No real account was changed.'}
            </p>
            <Link
              className="button-link"
              to={
                kind === 'register'
                  ? '/verify-email'
                  : kind === 'forgot-password'
                    ? '/reset-password'
                    : '/login'
              }
            >
              {kind === 'register'
                ? 'Preview verification'
                : kind === 'forgot-password'
                  ? 'Preview password reset'
                  : 'Back to sign in'}
              <Icon name="arrow" />
            </Link>
            <p className="field-help">
              Need another link?{' '}
              <Link to="/resend-verification">Request verification</Link> or{' '}
              <Link to="/forgot-password">reset your password</Link>.
            </p>
          </div>
        ) : (
          <>
            <p className="auth-description muted">{copy.description}</p>
            {fixture ? (
              <p className="notice compact-notice">
                Demo only. Use sample details, never a real password.
              </p>
            ) : (
              <p className="notice compact-notice">
                Account access is not connected yet. You can still shorten links
                as a guest.
              </p>
            )}
            {needToken && !token && (
              <div className="notice">
                <div>
                  <strong>Your email link is missing.</strong>
                  <p>
                    Open the full link from your email, or request a new one.
                  </p>
                  {fixture && (
                    <Button
                      className="button-secondary button-small"
                      onClick={() => setToken('demo-token')}
                    >
                      Load demo email link
                    </Button>
                  )}
                </div>
              </div>
            )}
            <form noValidate onSubmit={(e) => void submit(e)}>
              {needEmail && (
                <Field
                  id="email"
                  name="email"
                  label="Email address"
                  type="email"
                  autoComplete="email"
                  autoCapitalize="none"
                  placeholder="you@example.com"
                  required
                  value={email}
                  error={fields.email}
                  disabled={busy || !fixture}
                  onChange={(e) => setEmail(e.target.value)}
                />
              )}
              {needPassword && (
                <div>
                  <Field
                    id="password"
                    name="password"
                    label={
                      kind === 'reset-password' ? 'New password' : 'Password'
                    }
                    type={show ? 'text' : 'password'}
                    autoComplete={
                      kind === 'login' ? 'current-password' : 'new-password'
                    }
                    required
                    value={password}
                    hint="12–128 characters. Password managers and paste are welcome."
                    error={fields.password}
                    disabled={busy || !fixture}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <div className="password-options">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={show}
                        onChange={(e) => setShow(e.target.checked)}
                      />
                      Show password
                    </label>
                    {kind === 'login' && (
                      <Link to="/forgot-password">Forgot password?</Link>
                    )}
                  </div>
                </div>
              )}
              {error ? <ErrorNotice error={error} /> : null}
              {error instanceof ApiError &&
                error.code === 'email_unverified' && (
                  <Link className="text-link" to="/resend-verification">
                    Request a verification email
                    <Icon name="arrow" />
                  </Link>
                )}
              <Button
                type="submit"
                className="button-primary"
                disabled={busy || !fixture || (needToken && !token)}
              >
                {busy ? 'Please wait…' : copy.action}
                <Icon name="arrow" />
              </Button>
            </form>
            {kind === 'login' && (
              <>
                <p className="auth-switch">
                  New around here? <Link to="/register">Create an account</Link>
                </p>
                {fixture && (
                  <div className="demo-entry">
                    <p>Just having a look?</p>
                    <Button
                      className="button-secondary"
                      onClick={() => {
                        onLogin('demo@example.com');
                        navigate(safeReturn(params.get('next')));
                      }}
                    >
                      Explore demo workspace
                      <Icon name="arrow" />
                    </Button>
                  </div>
                )}
              </>
            )}
            {kind === 'register' && (
              <p className="auth-switch">
                Already have an account? <Link to="/login">Sign in</Link>
              </p>
            )}
            {(kind === 'login' || kind === 'register') && (
              <p className="field-help google-note">
                Google sign-in is not available yet.
              </p>
            )}
            {needToken && (
              <Link
                className="text-link"
                to={
                  kind === 'reset-password'
                    ? '/forgot-password'
                    : '/resend-verification'
                }
              >
                Request a new link
                <Icon name="arrow" />
              </Link>
            )}
            {kind === 'forgot-password' && (
              <Link className="text-link" to="/login">
                Back to sign in
              </Link>
            )}
          </>
        )}
      </div>
    </section>
  );
}
