import type { CreatedLink } from './contracts';
import { ApiError } from './errors';

function invalid(): never {
  throw new ApiError(
    'invalid_response',
    'The service returned invalid link data.',
    201,
    'unknown',
    {},
    null,
    true,
  );
}
function httpUrl(value: unknown): string {
  if (typeof value !== 'string') return invalid();
  try {
    const url = new URL(value);
    if (
      !['https:', 'http:'].includes(url.protocol) ||
      url.username ||
      url.password
    )
      return invalid();
    return value;
  } catch {
    return invalid();
  }
}
function timestamp(value: unknown): string {
  if (
    typeof value !== 'string' ||
    !/^\d{4}-\d{2}-\d{2}T.*(?:Z|[+-]\d{2}:\d{2})$/.test(value) ||
    !Number.isFinite(Date.parse(value))
  )
    return invalid();
  return value;
}
export function adaptCreatedLink(body: unknown): CreatedLink {
  if (!body || typeof body !== 'object' || Array.isArray(body))
    return invalid();
  const wire = body as Record<string, unknown>;
  if (
    typeof wire.id !== 'number' ||
    !Number.isInteger(wire.id) ||
    wire.id < 0 ||
    typeof wire.short_code !== 'string' ||
    !/^[A-Za-z0-9-]{1,64}$/.test(wire.short_code)
  )
    return invalid();
  const shortUrl = httpUrl(wire.short_url);
  const publicUrl = new URL(shortUrl);
  if (
    !publicUrl.pathname.endsWith(`/${wire.short_code}`) ||
    publicUrl.search ||
    publicUrl.hash
  )
    return invalid();
  return {
    linkId: Number.isSafeInteger(wire.id) ? String(wire.id) : null,
    shortCode: wire.short_code,
    shortUrl,
    destination: httpUrl(wire.destination),
    expiresAt: wire.expires_at === null ? null : timestamp(wire.expires_at),
    createdAt: timestamp(wire.created_at),
  };
}
