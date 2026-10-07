export type ErrorEnvelope = 'domain' | 'validation' | 'detail' | 'unknown';
export class ApiError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status = 0,
    public readonly envelope: ErrorEnvelope = 'unknown',
    public readonly fields: Record<string, string> = {},
    public readonly retryAfter: number | null = null,
    public readonly outcomeUnknown = false,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

const messages: Record<string, string> = {
  alias_taken: 'This alias is taken. Choose another alias.',
  invalid_alias: 'Use 3–64 letters, numbers, or hyphens for the alias.',
  invalid_expiry: 'Choose a future expiry time.',
  invalid_credentials: 'Check your email and password.',
  email_unverified: 'Verify your email before signing in.',
  account_locked: 'This account is temporarily locked. Try again later.',
  email_taken: 'This email is already registered.',
  invalid_refresh_token: 'Your session expired. Sign in again.',
  invalid_or_expired_token:
    'This link is invalid or expired. Request a new link.',
};

export function httpError(
  status: number,
  body: unknown,
  retry: string | null,
  mutation: boolean,
): ApiError {
  let envelope: ErrorEnvelope = 'unknown';
  let code = 'http_error';
  const fields: Record<string, string> = {};
  if (body && typeof body === 'object' && !Array.isArray(body)) {
    const data = body as Record<string, unknown>;
    if (typeof data.error === 'string' && typeof data.message === 'string') {
      envelope = 'domain';
      if (/^[a-z_]{1,64}$/.test(data.error)) code = data.error;
    } else if (Array.isArray(data.detail)) {
      envelope = 'validation';
      for (const item of data.detail) {
        if (
          !item ||
          typeof item !== 'object' ||
          !('loc' in item) ||
          !Array.isArray(item.loc)
        )
          continue;
        const field: unknown = item.loc.at(-1);
        if (
          typeof field === 'string' &&
          [
            'destination',
            'alias',
            'expires_at',
            'email',
            'password',
            'new_password',
          ].includes(field)
        )
          fields[field] = 'Check this value.';
      }
    } else if (typeof data.detail === 'string') envelope = 'detail';
  }
  const fallback: Record<number, string> = {
    400: 'Check the request and try again.',
    401: 'Your session expired. Sign in again.',
    403: 'This action is unavailable for your account.',
    404: 'This item is unavailable.',
    409: 'This request conflicts with an existing item.',
    422: 'Check the form values.',
    423: 'This account is temporarily locked. Try again later.',
    429: 'Too many requests. Wait before trying again.',
    503: 'The service is unavailable. Try again later.',
  };
  const seconds = retry && /^\d+$/.test(retry) ? Number(retry) : NaN;
  const retryAfter =
    Number.isSafeInteger(seconds) && seconds > 0 && seconds <= 86400
      ? seconds
      : null;
  return new ApiError(
    code,
    status >= 500
      ? (fallback[status] ?? 'The service could not complete the request.')
      : (messages[code] ??
          fallback[status] ??
          'The request could not be completed.'),
    status,
    envelope,
    fields,
    retryAfter,
    mutation && status >= 500,
  );
}
