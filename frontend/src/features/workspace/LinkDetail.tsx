import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from 'react';
import { Link, useNavigate, useParams } from 'react-router';
import type { ProductGateway, SavedLink } from '../../lib/api/contracts';
import { useResource } from '../../lib/useResource';
import { linkStatus, localDateInput, validateLink } from '../../lib/validation';
import { Button } from '../../components/ui/Button';
import { Field } from '../../components/ui/Field';
import { Icon } from '../../components/ui/Icon';
import { Modal } from '../../components/ui/Modal';
import { ErrorNotice, Loading } from '../../components/ui/Feedback';
import { LinkActions } from '../shorten/LinkActions';

function Editor({
  link,
  links,
  saved,
}: {
  link: SavedLink;
  links: ProductGateway;
  saved: () => void;
}) {
  const [destination, setDestination] = useState(link.destination);
  const [expiry, setExpiry] = useState(localDateInput(link.expiresAt));
  const [active, setActive] = useState(link.active);
  const [fields, setFields] = useState<Record<string, string>>({});
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const pending = useRef<AbortController | null>(null);
  useEffect(() => () => pending.current?.abort(), []);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending.current) return;
    const check = validateLink(destination, '', expiry);
    setFields(check.fields);
    setError(null);
    if (Object.keys(check.fields).length) {
      event.currentTarget
        .querySelector<HTMLInputElement>(
          '[name="' + Object.keys(check.fields)[0] + '"]',
        )
        ?.focus();
      return;
    }
    const controller = new AbortController();
    pending.current = controller;
    setBusy(true);
    try {
      await links.update(
        link.linkId,
        {
          destination: check.input.destination,
          expiresAt: check.input.expiresAt ?? null,
          active,
        },
        controller.signal,
      );
      if (!controller.signal.aborted) saved();
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
    <form className="edit-form" noValidate onSubmit={(e) => void submit(e)}>
      <h2>Where it goes</h2>
      <Field
        id="edit-destination"
        name="destination"
        label="Destination URL"
        type="url"
        required
        value={destination}
        disabled={busy}
        error={fields.destination}
        onChange={(e) => setDestination(e.target.value)}
      />
      <Field
        id="edit-expiry"
        name="expires_at"
        label="Expiry date and time"
        type="datetime-local"
        value={expiry}
        disabled={busy}
        error={fields.expires_at}
        hint={`Optional. Leave empty for no expiry. Timezone: ${Intl.DateTimeFormat().resolvedOptions().timeZone}.`}
        onChange={(e) => setExpiry(e.target.value)}
      />
      <label className="checkbox-label">
        <input
          type="checkbox"
          checked={active}
          disabled={busy}
          onChange={(e) => setActive(e.target.checked)}
        />
        Link enabled
      </label>
      <p className="field-help">
        Pause a link without deleting it. This setting affects the demo only.
      </p>
      {error ? <ErrorNotice error={error} /> : null}
      <Button type="submit" disabled={busy}>
        {busy ? 'Saving…' : 'Save changes'}
        <Icon name="check" />
      </Button>
    </form>
  );
}
export function LinkDetail({
  links,
  revision,
}: {
  links: ProductGateway;
  revision: number;
}) {
  const { id = '' } = useParams();
  const navigate = useNavigate();
  const load = useCallback(
    (signal: AbortSignal) => {
      void revision;
      return links.get(id, signal);
    },
    [links, id, revision],
  );
  const { data, error, loading, reload } = useResource(load);
  const [confirm, setConfirm] = useState(false);
  const [busy, setBusy] = useState(false);
  const [deleteError, setDeleteError] = useState<unknown>(null);
  const [message, setMessage] = useState('');
  const pending = useRef<AbortController | null>(null);
  useEffect(() => () => pending.current?.abort(), []);
  async function remove() {
    if (pending.current) return;
    const controller = new AbortController();
    pending.current = controller;
    setBusy(true);
    setDeleteError(null);
    try {
      await links.remove(id, controller.signal);
      if (!controller.signal.aborted) navigate('/dashboard', { replace: true });
    } catch (e) {
      if (!controller.signal.aborted) setDeleteError(e);
    } finally {
      if (pending.current === controller) {
        pending.current = null;
        setBusy(false);
      }
    }
  }
  return (
    <>
      <Link to="/dashboard" className="back-link">
        <Icon name="back" size={17} />
        All links
      </Link>
      <div className="page-heading">
        <div>
          <h1>Link details</h1>
          <p className="muted">Small edits. A new direction.</p>
        </div>
        {data && (
          <Link
            className="button-link button-secondary"
            to={`/dashboard/urls/${id}/analytics`}
          >
            View analytics
            <Icon name="chart" />
          </Link>
        )}
      </div>
      {loading ? (
        <Loading label="Loading link details…" />
      ) : error ? (
        <ErrorNotice error={error} retry={reload} />
      ) : (
        data && (
          <>
            <section className="link-summary">
              <div>
                <span
                  className={`status-label status-${linkStatus(data).toLowerCase()}`}
                >
                  <span aria-hidden="true" />
                  {linkStatus(data)}
                </span>
                <h2 className="mono break-word">/{data.shortCode}</h2>
                <p className="muted break-word">{data.shortUrl}</p>
              </div>
              <LinkActions key={data.shortUrl} link={data} links={links} />
            </section>
            {message && (
              <p className="notice notice-success" role="status">
                <Icon name="check" />
                {message}
              </p>
            )}
            <div className="detail-grid">
              <Editor
                key={`${data.destination}-${data.expiresAt}-${data.active}`}
                link={data}
                links={links}
                saved={() => {
                  setMessage('Demo changes saved for this session.');
                  reload();
                }}
              />
              <aside className="detail-meta">
                <h2>The little details</h2>
                <dl>
                  <dt>Created</dt>
                  <dd>
                    {new Date(data.createdAt).toLocaleDateString('en', {
                      dateStyle: 'medium',
                      timeZone: 'UTC',
                    })}{' '}
                    · UTC
                  </dd>
                  <dt>Lifetime sample clicks</dt>
                  <dd>{data.clicks.toLocaleString()}</dd>
                  <dt>Short code</dt>
                  <dd className="mono break-word">{data.shortCode}</dd>
                </dl>
                <p className="field-help">
                  The short code stays the same when you change the destination.
                </p>
              </aside>
            </div>
            <section className="danger-zone">
              <div>
                <h2>Time to let this one go?</h2>
                <p>
                  Deletion removes this link from the demo workspace. You cannot
                  undo it.
                </p>
              </div>
              <Button
                className="button-danger"
                onClick={() => {
                  setConfirm(true);
                  setDeleteError(null);
                }}
              >
                Delete link
                <Icon name="trash" />
              </Button>
            </section>
            <Modal
              open={confirm}
              onOpenChange={(value) => {
                if (!busy) setConfirm(value);
              }}
              title="Delete this link?"
              description={`Remove /${data.shortCode} from your demo workspace. This action cannot be undone.`}
            >
              {deleteError ? <ErrorNotice error={deleteError} /> : null}
              <div className="modal-actions">
                <Button
                  className="button-secondary"
                  disabled={busy}
                  onClick={() => setConfirm(false)}
                >
                  Cancel
                </Button>
                <Button
                  className="button-danger"
                  disabled={busy}
                  onClick={() => void remove()}
                >
                  {busy ? 'Deleting…' : 'Delete link'}
                </Button>
              </div>
            </Modal>
          </>
        )
      )}
    </>
  );
}
