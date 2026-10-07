import { createServer, type Server } from 'node:http';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { request } from './client';

let server: Server;
let base: string;
beforeAll(async () => {
  server = createServer((req, res) => {
    res.setHeader('Content-Type', 'application/json');
    switch (req.url) {
      case '/domain':
        res.writeHead(409);
        res.end(
          JSON.stringify({
            error: 'alias_taken',
            message: 'Alias is already taken',
          }),
        );
        break;
      case '/detail':
        res.writeHead(422);
        res.end(
          JSON.stringify({
            detail: [
              {
                loc: ['body', 'destination'],
                msg: 'private payload',
                input: 'secret',
              },
            ],
          }),
        );
        break;
      case '/limited':
        res.writeHead(429, { 'Retry-After': '37' });
        res.end(JSON.stringify({ detail: 'Rate limit exceeded' }));
        break;
      case '/empty':
        res.writeHead(204);
        res.end();
        break;
      case '/accepted':
        res.writeHead(202);
        res.end();
        break;
      case '/broken':
        res.end('<html>private trace</html>');
        break;
      case '/unavailable':
        res.writeHead(503);
        res.end(
          JSON.stringify({ detail: 'Internal database connection secret' }),
        );
        break;
      case '/slow':
        setTimeout(() => res.end('{}'), 100);
        break;
      default:
        res.end(
          JSON.stringify({ authorization: req.headers.authorization ?? null }),
        );
    }
  });
  await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve));
  const address = server.address();
  if (!address || typeof address === 'string')
    throw new Error('Missing test address');
  base = `http://127.0.0.1:${address.port}`;
});
afterAll(async () => {
  server.closeAllConnections();
  await new Promise<void>((resolve) => server.close(() => resolve()));
});

describe('HTTP boundary against a real loopback server', () => {
  it('keeps domain and validation envelopes distinct without displaying raw input', async () => {
    await expect(
      request(`${base}/domain`, { method: 'POST', body: {} }),
    ).rejects.toMatchObject({
      status: 409,
      code: 'alias_taken',
      envelope: 'domain',
      outcomeUnknown: false,
    });
    await expect(
      request(`${base}/detail`, { method: 'POST', body: {} }),
    ).rejects.toMatchObject({
      status: 422,
      envelope: 'validation',
      fields: { destination: 'Check this value.' },
    });
  });
  it('preserves Retry-After and handles empty 202/204 bodies', async () => {
    await expect(request(`${base}/limited`)).rejects.toMatchObject({
      status: 429,
      retryAfter: 37,
      envelope: 'detail',
    });
    await expect(
      request(`${base}/empty`, { method: 'POST' }),
    ).resolves.toBeNull();
    await expect(
      request(`${base}/accepted`, { method: 'POST' }),
    ).resolves.toBeNull();
  });
  it('rejects malformed success and hides internal failure details', async () => {
    await expect(
      request(`${base}/broken`, { method: 'POST' }),
    ).rejects.toMatchObject({ code: 'invalid_response', outcomeUnknown: true });
    await expect(
      request(`${base}/unavailable`, { method: 'POST' }),
    ).rejects.toMatchObject({
      status: 503,
      message: 'The service is unavailable. Try again later.',
      outcomeUnknown: true,
    });
  });
  it('times out a mutation without claiming a known failure and cancels an obsolete read', async () => {
    await expect(
      request(`${base}/slow`, { method: 'POST', timeoutMs: 10 }),
    ).rejects.toMatchObject({ code: 'timeout', outcomeUnknown: true });
    const controller = new AbortController();
    const pending = request(`${base}/slow`, { signal: controller.signal });
    controller.abort();
    await expect(pending).rejects.toMatchObject({
      code: 'cancelled',
      outcomeUnknown: false,
    });
  });
  it('attaches credentials only through an explicit token seam', async () => {
    await expect(request(`${base}/echo`)).resolves.toEqual({
      authorization: null,
    });
    await expect(
      request(`${base}/echo`, { accessToken: 'test-access-token' }),
    ).resolves.toEqual({ authorization: 'Bearer test-access-token' });
  });
});
