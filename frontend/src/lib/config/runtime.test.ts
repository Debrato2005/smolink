import { describe, expect, it } from 'vitest';
import { readConfig } from './runtime';

describe('data source configuration', () => {
  it('never uses fixtures implicitly and refuses them in production', () => {
    expect(readConfig({}, false).source).toBe('live');
    expect(() => readConfig({ VITE_DATA_SOURCE: 'fixture' }, true)).toThrow();
    expect(() => readConfig({ VITE_DATA_SOURCE: 'fxture' }, false)).toThrow();
  });
  it('rejects credential-bearing or insecure remote API URLs', () => {
    for (const base of [
      'https://user:secret@example.com/api/v1',
      'http://example.com/api/v1',
      '//evil.test/api/v1',
      '/other',
      'https://example.com/api/v1?token=secret',
    ]) {
      expect(() => readConfig({ VITE_API_BASE_URL: base }, true)).toThrow();
    }
    expect(
      readConfig({ VITE_API_BASE_URL: 'https://api.example.com/api/v1' }, true)
        .apiBase,
    ).toBe('https://api.example.com/api/v1');
  });
});
