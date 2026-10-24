import { expect, it } from 'vitest';
import { validateLink } from './validation';

it('rejects destinations that exceed storage after URL normalization', () => {
  const prefix = 'https://example.com/';
  expect(
    validateLink(prefix + 'a'.repeat(2048 - prefix.length)).fields,
  ).toEqual({});
  expect(
    validateLink(prefix + 'a'.repeat(2049 - prefix.length)).fields.destination,
  ).toBeDefined();
  expect(
    validateLink(prefix + 'é'.repeat(400)).fields.destination,
  ).toBeDefined();
});

it('rejects impossible expiry dates instead of silently changing the day', () => {
  for (const expiry of ['2099-02-30T12:30', '2099-04-31T12:30']) {
    const result = validateLink('https://example.com/', '', expiry);
    expect(result.fields.expires_at).toBeDefined();
    expect(result.input.expiresAt).toBeUndefined();
  }
  expect(
    validateLink('https://example.com/', '', '2096-02-29T12:30').fields,
  ).toEqual({});
});
