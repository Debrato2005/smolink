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
    <div className="loading-state" role="status">
      <span className="loading-square" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}
