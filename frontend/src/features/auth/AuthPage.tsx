import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router';
import type { AccountAction, ProductGateway } from '../../lib/api/contracts';
import { ApiError } from '../../lib/api/errors';
import { safeReturn } from '../../lib/validation';
import { Button } from '../../components/ui/Button';
import { Field } from '../../components/ui/Field';
import { Icon } from '../../components/ui/Icon';
import { ErrorNotice } from '../../components/ui/Feedback';

// Google's multicolor G mark, as its sign-in branding guidelines require.
function GoogleMark() {
  return (
    <svg width="20" height="20" viewBox="0 0 48 48" aria-hidden="true">
      <path
        fill="#EA4335"
        d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
      />
      <path
        fill="#4285F4"
        d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
      />
      <path
        fill="#FBBC05"
        d="M10.53 28.59A14.5 14.5 0 0 1 9.5 24c0-1.59.28-3.14.76-4.59l-7.98-6.19A23.94 23.94 0 0 0 0 24c0 3.87.92 7.53 2.56 10.78l7.97-6.19z"
      />
      <path
        fill="#34A853"
        d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
      />
    </svg>
  );
}

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
  async function google() {
    if (pending.current) return;
    const controller = new AbortController();
    pending.current = controller;
    setBusy(true);
    setError(null);
    try {
      await links.account('google', {}, controller.signal);
      if (controller.signal.aborted) return;
      onLogin('you@gmail.com');
      navigate(safeReturn(params.get('next')), { replace: true });
    } catch (e) {
      if (!controller.signal.aborted) setError(e);
    } finally {
      if (pending.current === controller) {
        pending.current = null;
        setBusy(false);
      }
    }
  }
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
  const inbox =
    kind === 'register' ||
    kind === 'forgot-password' ||
    kind === 'resend-verification';
  const social = kind === 'login' || kind === 'register';
  return (
    <section className="auth-layout container">
      <aside className="auth-poster">
        <p className="poster-display">
          Every link,
          <br />
          kept in one
          <br />
          place.
        </p>
        <div className="poster-stubs" aria-hidden="true">
          <span className="mono">/portfolio</span>
          <span className="mono">/launch-notes</span>
          <span className="mono">/summer-playlist</span>
        </div>
        <p className="poster-note">
          Your links, their edits, and their clicks in one workspace.
        </p>
      </aside>
      <div className="auth-content">
        <Link to="/" className="back-link">
          <Icon name="back" size={17} />
          Back to Smolink
        </Link>
        <h1>
          {done
            ? inbox
              ? 'Check your inbox'
              : kind === 'verify-email'
                ? 'Email verified'
                : 'Password reset'
            : copy.title}
        </h1>
        {done ? (
          <div className="auth-success">
            <span className="success-mark">
              <Icon name={inbox ? 'mail' : 'check'} size={30} />
            </span>
            <p role="status">
              {kind === 'register'
                ? 'We sent you a verification link. Open it to finish creating your account.'
                : inbox
                  ? 'If an account uses that email, a new link is on its way. It can take a few minutes.'
                  : kind === 'verify-email'
                    ? 'Your email is verified. You can sign in now.'
                    : 'Your password is reset. Sign in with the new one.'}
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
                ? 'I have the link'
                : kind === 'forgot-password'
                  ? 'I have the reset link'
                  : 'Go to sign in'}
              <Icon name="arrow" />
            </Link>
            <p className="field-help">
              No email?{' '}
              <Link to="/resend-verification">Request verification</Link> or{' '}
              <Link to="/forgot-password">reset your password</Link>.
            </p>
          </div>
        ) : (
          <>
            <p className="auth-description muted">{copy.description}</p>
            {!fixture && (
              <p className="notice compact-notice">
                Accounts are coming soon. You can shorten links without one
                today.
              </p>
            )}
            {social && (
              <>
                <Button
                  className="button-google"
                  disabled={busy || !fixture}
                  onClick={() => void google()}
                >
                  <GoogleMark />
                  Continue with Google
                </Button>
                <p className="auth-divider">
                  <span>or use your email</span>
                </p>
              </>
            )}
            {needToken && !token && (
              <div className="notice">
                <div>
                  <strong>Your email link is missing.</strong>
                  <p>
                    Open the full link from your email, or request a new one.
                  </p>
                  {import.meta.env.DEV && fixture && (
                    <Button
                      className="button-secondary button-small"
                      onClick={() => setToken('test-token')}
                    >
                      Use test link
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
                {import.meta.env.DEV && fixture && (
                  <div className="dev-entry">
                    <Button
                      className="button-secondary button-small"
                      onClick={() => {
                        onLogin('test@example.com');
                        navigate(safeReturn(params.get('next')));
                      }}
                    >
                      Use test account
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
