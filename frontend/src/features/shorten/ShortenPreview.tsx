import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Button } from '../../components/ui/Button';
import { Field } from '../../components/ui/Field';
import { Icon } from '../../components/ui/Icon';
import { ErrorNotice } from '../../components/ui/Feedback';
import type { CreatedLink, ProductGateway } from '../../lib/api/contracts';
import { ApiError } from '../../lib/api/errors';
import { validateLink } from '../../lib/validation';
import { LinkActions } from './LinkActions';

type State =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'ready'; link: CreatedLink }
  | { kind: 'error'; error: unknown };
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
  return (
    <section
      className="create-panel"
      id="shorten"
      aria-labelledby="create-heading"
    >
      <div className="panel-title">
        <h2 id="create-heading">Make it smol.</h2>
        <Icon name="link" size={26} />
      </div>
      <p className="muted">A long URL goes in. A little link comes out.</p>
      <form ref={form} noValidate onSubmit={(e) => void submit(e)}>
        <Field
          id="destination"
          name="destination"
          label="Destination URL"
          type="url"
          autoComplete="url"
          required
          placeholder="https://your-very-long-link.com"
          value={destination}
          disabled={busy}
          error={fields.destination}
          onChange={(e) => {
            setDestination(e.target.value);
            clear();
          }}
        />
        <Field
          id="alias"
          name="alias"
          label="Custom alias"
          hint="Optional · 3–64 letters, numbers, or hyphens."
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
          <Icon name="clock" size={18} />
          Set an expiry <span className="muted">(optional)</span>
        </label>
        {hasExpiry && (
          <Field
            id="expiry"
            name="expires_at"
            type="datetime-local"
            label="Expiry date and time"
            hint={`Your timezone: ${Intl.DateTimeFormat().resolvedOptions().timeZone}.`}
            value={expiry}
            disabled={busy}
            error={fields.expires_at}
            onChange={(e) => {
              setExpiry(e.target.value);
              clear();
            }}
          />
        )}
        <Button
          type="submit"
          className="button-primary"
          disabled={busy}
          aria-busy={busy}
        >
          {busy ? 'Shortening…' : 'Shorten URL'}
          <Icon name="arrow" />
        </Button>
        <p className="form-footnote">
          {links.source === 'fixture'
            ? 'Demo preview. Sample links do not redirect.'
            : 'No account needed. Redirect service is not connected yet.'}
        </p>
      </form>
      {busy && (
        <p className="sr-only" role="status">
          Creating your link…
        </p>
      )}
      {state.kind === 'error' && <ErrorNotice error={state.error} />}
      {state.kind === 'ready' && (
        <div className="result-panel">
          <p className="result-title" role="status">
            <Icon name="check" />
            {links.source === 'fixture' ? 'Demo link ready' : 'Link created'}
          </p>
          <label htmlFor="short-url">Short URL</label>
          <input
            id="short-url"
            className="mono"
            readOnly
            value={state.link.shortUrl}
            onFocus={(e) => e.target.select()}
          />
          <LinkActions
            key={state.link.shortUrl}
            link={state.link}
            links={links}
          />
        </div>
      )}
    </section>
  );
}
