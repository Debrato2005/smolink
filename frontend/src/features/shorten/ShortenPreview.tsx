import {
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type FormEvent,
} from 'react';
import { Button } from '../../components/ui/Button';
import { Field } from '../../components/ui/Field';
import { Icon } from '../../components/ui/Icon';
import { ErrorNotice } from '../../components/ui/Feedback';
import type { CreatedLink, ProductGateway } from '../../lib/api/contracts';
import { ApiError } from '../../lib/api/errors';
import { characters, validateLink } from '../../lib/validation';
import { LinkActions } from './LinkActions';

type State =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'ready'; link: CreatedLink }
  | { kind: 'error'; error: unknown };

const zone = Intl.DateTimeFormat().resolvedOptions().timeZone;

function Ticket({ link, links }: { link: CreatedLink; links: ProductGateway }) {
  const resultInput = useRef<HTMLInputElement>(null);
  useEffect(() => {
    const input = resultInput.current;
    if (!input) return;
    input.focus({ preventScroll: true });
    const bounds = input.getBoundingClientRect();
    const headerBottom =
      document.querySelector('.site-header')?.getBoundingClientRect().bottom ??
      0;
    if (bounds.top < headerBottom || bounds.bottom > window.innerHeight)
      input.scrollIntoView({ block: 'center' });
  }, []);
  const before = characters(link.destination);
  const after = characters(link.shortUrl);
  const saved = before - after;
  return (
    <div className="ticket ticket-result">
      <div className="ticket-stub">
        <Icon name="scissors" size={22} />
        <strong className="ticket-count">{Math.abs(saved)}</strong>
        <span>{saved >= 0 ? 'characters cut' : 'characters added'}</span>
      </div>
      <div className="ticket-body">
        <p className="ticket-status" role="status">
          <Icon name="check" />
          Your link is ready
        </p>
        <label htmlFor="short-url">Short URL</label>
        <input
          id="short-url"
          className="ticket-url mono"
          style={{ '--chars': after } as CSSProperties}
          readOnly
          ref={resultInput}
          value={link.shortUrl}
          onFocus={(e) => e.target.select()}
        />
        <p className="ticket-meta">
          {saved >= 0
            ? `${before} characters became ${after}.`
            : `Your alias made it ${-saved} characters longer than the original.`}
          {link.expiresAt &&
            ` Expires ${new Date(link.expiresAt).toLocaleString('en', {
              dateStyle: 'medium',
              timeStyle: 'short',
            })} (${zone}).`}
        </p>
        <LinkActions key={link.shortUrl} link={link} links={links} />
      </div>
    </div>
  );
}

export function ShortenPreview({
  links,
  onCreated,
}: {
  links: ProductGateway;
  onCreated?: (() => void) | undefined;
}) {
  const [destination, setDestination] = useState('');
  const [alias, setAlias] = useState('');
  const [expiry, setExpiry] = useState('');
  const [hasExpiry, setHasExpiry] = useState(false);
  const [fields, setFields] = useState<Record<string, string>>({});
  const [state, setState] = useState<State>({ kind: 'idle' });
  const pending = useRef<AbortController | null>(null);
  const form = useRef<HTMLFormElement>(null);
  useEffect(() => () => pending.current?.abort(), []);
  function clear() {
    setState({ kind: 'idle' });
    setFields({});
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending.current) return;
    const checked = validateLink(destination, alias, hasExpiry ? expiry : '');
    if (hasExpiry && !expiry)
      checked.fields.expires_at = 'Choose an expiry date and time.';
    setFields(checked.fields);
    if (Object.keys(checked.fields).length) {
      const first = Object.keys(checked.fields)[0];
      form.current
        ?.querySelector<HTMLInputElement>(`[name="${first}"]`)
        ?.focus();
      return;
    }
    const controller = new AbortController();
    pending.current = controller;
    setState({ kind: 'loading' });
    try {
      const link = await links.create(checked.input, controller.signal);
      if (!controller.signal.aborted) {
        setState({ kind: 'ready', link });
        onCreated?.();
      }
    } catch (error) {
      if (controller.signal.aborted) return;
      if (error instanceof ApiError) {
        const errors = { ...error.fields };
        if (error.code === 'alias_taken' || error.code === 'invalid_alias')
          errors.alias = error.message;
        if (error.code === 'invalid_expiry') errors.expires_at = error.message;
        setFields(errors);
      }
      setState({ kind: 'error', error });
    } finally {
      if (pending.current === controller) pending.current = null;
    }
  }
  const busy = state.kind === 'loading';
  const ready = state.kind === 'ready' ? state.link : null;
  return (
    <section className="bench" id="shorten" aria-labelledby="create-heading">
      <h2 id="create-heading" className="sr-only">
        Make it smol.
      </h2>
      <form ref={form} noValidate onSubmit={(e) => void submit(e)}>
        <Field
          id="destination"
          name="destination"
          label="Destination URL"
          type="url"
          inputMode="url"
          autoComplete="url"
          required
          placeholder="https://your-very-long-link.com/goes/here"
          value={destination}
          disabled={busy}
          error={fields.destination}
          onChange={(e) => {
            setDestination(e.target.value);
            clear();
          }}
          addon={
            <Button
              type="submit"
              className="button-ink"
              disabled={busy}
              aria-busy={busy}
            >
              {busy ? 'Shortening…' : 'Shorten URL'}
              <Icon name="arrow" />
            </Button>
          }
        />
        <div className="bench-options">
          <Field
            id="alias"
            name="alias"
            label="Custom alias (optional)"
            hint="3–64 letters, numbers, or hyphens. Saved in lowercase."
            placeholder="your-big-idea"
            autoCapitalize="none"
            autoCorrect="off"
            spellCheck={false}
            value={alias}
            disabled={busy}
            error={fields.alias}
            onChange={(e) => {
              setAlias(e.target.value);
              clear();
            }}
          />
          <div className="expiry-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={hasExpiry}
                disabled={busy}
                onChange={(e) => {
                  setHasExpiry(e.target.checked);
                  clear();
                }}
              />
              Set an expiry
            </label>
            {hasExpiry && (
              <Field
                id="expiry"
                name="expires_at"
                type="datetime-local"
                label="Expiry date and time"
                hint={`Your timezone: ${zone}.`}
                value={expiry}
                disabled={busy}
                error={fields.expires_at}
                onChange={(e) => {
                  setExpiry(e.target.value);
                  clear();
                }}
              />
            )}
          </div>
        </div>
        <p className="form-footnote">
          {links.source === 'fixture'
            ? 'Free. No account needed.'
            : 'Free. No account needed. Short links start redirecting when the redirect service launches.'}
        </p>
      </form>
      {busy && (
        <p className="sr-only" role="status">
          Creating your link…
        </p>
      )}
      {state.kind === 'error' && <ErrorNotice error={state.error} />}
      {ready && <Ticket link={ready} links={links} />}
    </section>
  );
}
