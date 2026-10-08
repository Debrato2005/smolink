import { useEffect, useRef, useState } from 'react';
import type { CreatedLink, ProductGateway } from '../../lib/api/contracts';
import { Button } from '../../components/ui/Button';
import { Icon } from '../../components/ui/Icon';
import { Modal } from '../../components/ui/Modal';
import { ErrorNotice } from '../../components/ui/Feedback';

export function LinkActions({
  link,
  links,
  compact = false,
}: {
  link: CreatedLink;
  links: ProductGateway;
  compact?: boolean;
}) {
  const [copy, setCopy] = useState<'idle' | 'copied' | 'denied'>('idle');
  const [open, setOpen] = useState(false);
  const [qr, setQr] = useState('');
  const [error, setError] = useState<unknown>(null);
  const pending = useRef<AbortController | null>(null);
  const copyBusy = useRef(false);
  const alive = useRef(true);
  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
      pending.current?.abort();
    };
  }, []);
  async function copyLink() {
    if (copyBusy.current) return;
    copyBusy.current = true;
    try {
      await navigator.clipboard.writeText(link.shortUrl);
      if (alive.current) setCopy('copied');
    } catch {
      if (alive.current) setCopy('denied');
    } finally {
      copyBusy.current = false;
    }
  }
  async function showQr() {
    if (pending.current) return;
    setOpen(true);
    setQr('');
    setError(null);
    const controller = new AbortController();
    pending.current = controller;
    try {
      const result = await links.qr(link, controller.signal);
      if (!controller.signal.aborted) setQr(result);
    } catch (e) {
      if (!controller.signal.aborted) setError(e);
    } finally {
      if (pending.current === controller) pending.current = null;
    }
  }
  return (
    <>
      <div className="link-actions">
        <Button
          className={
            compact ? 'button-secondary button-small' : 'button-secondary'
          }
          aria-label={compact ? `Copy ${link.shortCode}` : undefined}
          onClick={() => void copyLink()}
        >
          <Icon name={copy === 'copied' ? 'check' : 'copy'} />
          {copy === 'copied' ? 'Copied' : 'Copy link'}
        </Button>
        {!compact && (
          <Button
            className="button-secondary"
            disabled={links.source === 'live'}
            onClick={() => void showQr()}
          >
            <Icon name="qr" />
            View QR code
          </Button>
        )}
      </div>
      <span className="sr-only" role="status">
        {copy === 'copied' ? 'Link copied to clipboard.' : ''}
      </span>
      {copy === 'denied' && (
        <div className="manual-copy" role="alert">
          <p>
            Clipboard access was denied. Select and copy this link manually.
          </p>
          <input
            aria-label={`Copy ${link.shortCode} manually`}
            readOnly
            value={link.shortUrl}
            onFocus={(event) => event.target.select()}
          />
        </div>
      )}
      {!compact && links.source === 'live' && (
        <p className="field-help">QR codes are coming soon.</p>
      )}
      <Modal
        open={open}
        onOpenChange={(next) => {
          setOpen(next);
          if (!next) {
            pending.current?.abort();
            pending.current = null;
          }
        }}
        title="One scan. A little closer."
        description="Scan it to open your short link."
      >
        {error ? (
          <ErrorNotice error={error} retry={() => void showQr()} />
        ) : (
          <div className="qr-result">
            <div className="qr-preview">
              {qr ? (
                <img
                  src={qr}
                  alt="QR code for your short link"
                  width="256"
                  height="256"
                />
              ) : (
                <div
                  className="qr-loading"
                  role="status"
                  aria-label="Generating QR code…"
                >
                  <span className="sr-only">Generating QR code…</span>
                  <svg
                    className="skeleton qr-skeleton"
                    data-slot="skeleton"
                    viewBox="0 0 100 100"
                    aria-hidden="true"
                    focusable="false"
                  >
                    <g className="qr-skeleton-markers">
                      <rect x="13" y="13" width="24" height="24" rx="3" />
                      <rect x="63" y="13" width="24" height="24" rx="3" />
                      <rect x="13" y="63" width="24" height="24" rx="3" />
                    </g>
                    <g className="qr-skeleton-blocks">
                      <rect x="21" y="21" width="8" height="8" rx="1" />
                      <rect x="71" y="21" width="8" height="8" rx="1" />
                      <rect x="21" y="71" width="8" height="8" rx="1" />
                      <rect x="45" y="13" width="10" height="24" rx="2" />
                      <rect x="13" y="45" width="24" height="10" rx="2" />
                      <rect x="45" y="45" width="18" height="18" rx="2" />
                      <rect x="71" y="45" width="16" height="10" rx="2" />
                      <rect x="45" y="71" width="10" height="16" rx="2" />
                      <rect x="63" y="71" width="24" height="16" rx="2" />
                    </g>
                  </svg>
                </div>
              )}
            </div>
            <p className="mono break-word">{link.shortUrl}</p>
            {qr ? (
              <a
                className="button-link"
                href={qr}
                download={`smolink-${link.shortCode}.png`}
              >
                Download PNG
                <Icon name="arrow" />
              </a>
            ) : (
              <Button className="button-link" disabled>
                Download PNG
                <Icon name="arrow" />
              </Button>
            )}
            <p className="field-help">
              PNG · 1024 × 1024 px · Keep the white margin.
            </p>
          </div>
        )}
      </Modal>
    </>
  );
}
