import type { CreateLinkInput } from './api/contracts';
const reserved = new Set([
  'api',
  'docs',
  'health',
  'login',
  'me',
  'openapi.json',
  'redoc',
  'register',
]);
export function validateLink(destination: string, alias = '', expiry = '') {
  const fields: Record<string, string> = {};
  let normalized = destination.trim();
  try {
    const url = new URL(normalized);
    if (
      !['https:', 'http:'].includes(url.protocol) ||
      url.username ||
      url.password
    )
      throw new Error();
    normalized = url.href;
  } catch {
    fields.destination =
      'Enter a complete http:// or https:// URL without credentials.';
  }
  const normalizedAlias = alias.trim().toLowerCase();
  if (normalizedAlias && !/^[a-z0-9-]{3,64}$/.test(normalizedAlias))
    fields.alias = 'Use 3–64 letters, numbers, or hyphens.';
  else if (reserved.has(normalizedAlias))
    fields.alias = 'This alias is reserved. Choose another alias.';
  let expiresAt: string | undefined;
  if (expiry) {
    const date = new Date(expiry);
    if (!Number.isFinite(date.valueOf()) || date.valueOf() <= Date.now())
      fields.expires_at = 'Choose a future expiry time.';
    else expiresAt = date.toISOString();
  }
  const input: CreateLinkInput = {
    destination: normalized,
    ...(normalizedAlias ? { alias: normalizedAlias } : {}),
    ...(expiresAt ? { expiresAt } : {}),
  };
  return { fields, input };
}
export function localDateInput(value: string | null) {
  if (!value) return '';
  const date = new Date(value);
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16);
}
export function linkStatus(link: {
  active: boolean;
  expiresAt: string | null;
}) {
  return link.expiresAt && Date.parse(link.expiresAt) <= Date.now()
    ? 'Expired'
    : link.active
      ? 'Active'
      : 'Paused';
}
export function safeReturn(value: string | null) {
  return value &&
    /^\/dashboard(?:\/new|\/urls\/[A-Za-z0-9-]+(?:\/analytics)?)?(?:\?[^#\\]*)?$/.test(
      value,
    )
    ? value
    : '/dashboard';
}
