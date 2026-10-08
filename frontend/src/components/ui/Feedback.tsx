import { Link } from 'react-router';
import { ApiError } from '../../lib/api/errors';
import { Button } from './Button';
import { Icon } from './Icon';
export function ErrorNotice({
  error,
  retry,
}: {
  error: unknown;
  retry?: (() => void) | undefined;
}) {
  const failure = error instanceof ApiError ? error : null;
  return (
    <div className="notice notice-error" role="alert">
      <Icon name="info" />
      <div>
        <p>
          {failure?.message ?? 'Something went wrong. Try again later.'}
          {failure?.retryAfter ? ` Wait ${failure.retryAfter} seconds.` : ''}
          {failure?.outcomeUnknown
            ? ' The link may have been created. Check before submitting again.'
            : ''}
        </p>
        {failure?.status === 401 && (
          <Link className="text-link" to="/login">
            Sign in again
          </Link>
        )}
        {retry && (
          <Button className="button-secondary button-small" onClick={retry}>
            Try again
          </Button>
        )}
      </div>
    </div>
  );
}
export function Loading({ label = 'Loading your links…' }: { label?: string }) {
  return (
    <div className="skeleton-loading" role="status" aria-label={label}>
      <span className="sr-only">{label}</span>
      <div className="skeleton-metrics" aria-hidden="true">
        {[0, 1, 2].map((item) => (
          <div key={item} className="skeleton-card">
            <Skeleton className="skeleton-label" />
            <Skeleton className="skeleton-number" />
          </div>
        ))}
      </div>
      <div className="skeleton-panel" aria-hidden="true">
        {[0, 1, 2].map((item) => (
          <div key={item} className="skeleton-row">
            <Skeleton className="skeleton-line" />
            <Skeleton className="skeleton-line skeleton-line-short" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function Skeleton({ className = '' }: { className?: string }) {
  return (
    <div
      data-slot="skeleton"
      className={`skeleton ${className}`}
      aria-hidden="true"
    />
  );
}
