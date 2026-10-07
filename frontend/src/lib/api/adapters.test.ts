import { expect, it } from 'vitest';
import { adaptCreatedLink } from './adapters';

const wire = {
  id: 7,
  short_code: 'abc123',
  short_url: 'https://short.example/abc123',
  destination: 'https://example.com/',
  expires_at: null,
  created_at: '2026-10-05T10:00:00Z',
};
it('does not recover an unsafe Snowflake by stringifying a rounded number', () => {
  expect(
    adaptCreatedLink({ ...wire, id: 7440000000000000000 }).linkId,
  ).toBeNull();
  expect(adaptCreatedLink(wire).linkId).toBe('7');
});
it('rejects unsafe URLs, missing fields, and mismatched public code', () => {
  for (const changed of [
    { short_url: 'javascript:alert(1)' },
    { destination: 'data:text/html,bad' },
    { short_code: '' },
    { short_url: 'https://short.example/other' },
    { created_at: 'not-a-date' },
    { expires_at: 'not-a-date' },
  ]) {
    expect(() => adaptCreatedLink({ ...wire, ...changed })).toThrow();
  }
  expect(() => adaptCreatedLink({ short_code: 'abc123' })).toThrow();
});
