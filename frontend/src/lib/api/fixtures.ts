import { adaptCreatedLink } from './adapters';
import type { DemoScenario, ProductGateway, SavedLink } from './contracts';
import { ApiError, httpError } from './errors';

const names = [
  'portfolio',
  'launch-notes',
  'design-resources',
  'summer-playlist',
  'the-reading-list',
  'weekend-guide',
  'brand-kit',
  'studio-news',
  'event-tickets',
  'old-campaign',
  'press-pack',
  'project-notes',
];
function seed(): SavedLink[] {
  return names.map((name, i) => ({
    linkId: String(i + 1),
    shortCode: name,
    shortUrl: `https://smolink.invalid/${name}`,
    destination: `https://example.com/${name}/a-little-more-to-discover`,
    expiresAt: i === 9 ? '2026-08-01T00:00:00Z' : null,
    createdAt: new Date(Date.UTC(2026, 9, 6 - i, 9)).toISOString(),
    clicks: [1248, 862, 534, 326, 219, 108, 87, 62, 41, 28, 16, 0][i] ?? 0,
    active: i !== 10,
  }));
}
let rows = seed();
let scenario: DemoScenario = 'normal';
let sequence = 100;
async function wait(signal?: AbortSignal) {
  if (signal?.aborted)
    throw new ApiError('cancelled', 'The request was cancelled.');
  await new Promise<void>((resolve, reject) => {
    const cancel = () => {
      clearTimeout(timer);
      reject(new ApiError('cancelled', 'The request was cancelled.'));
    };
    const timer = setTimeout(() => {
      signal?.removeEventListener('abort', cancel);
      resolve();
    }, 280);
    signal?.addEventListener('abort', cancel, { once: true });
  });
  if (scenario === 'error') throw httpError(503, null, null, false);
  if (scenario === 'limited') throw httpError(429, null, '5', false);
  if (scenario === 'expired')
    throw httpError(
      401,
      { error: 'invalid_refresh_token', message: '' },
      null,
      false,
    );
}
function find(id: string) {
  const row = rows.find((item) => item.linkId === id);
  if (!row) throw httpError(404, null, null, false);
  return row;
}
export const fixtureLinks: ProductGateway = {
  source: 'fixture',
  setScenario(next) {
    scenario = next;
  },
  resetDemo() {
    rows = seed();
    scenario = 'normal';
    sequence = 100;
  },
  async create(input, signal) {
    await wait(signal);
    const code = input.alias?.toLowerCase() || `demo-${++sequence}`;
    if (rows.some((r) => r.shortCode === code))
      throw httpError(409, { error: 'alias_taken', message: '' }, null, true);
    const result = adaptCreatedLink({
      id: ++sequence,
      short_code: code,
      short_url: `https://smolink.invalid/${code}`,
      destination: input.destination,
      expires_at: input.expiresAt ?? null,
      created_at: new Date().toISOString(),
    });
    rows = [
      { ...result, linkId: String(sequence), clicks: 0, active: true },
      ...rows,
    ];
    return result;
  },
  async account(action, input, signal) {
    await wait(signal);
    if (action === 'login' && scenario === 'locked')
      throw httpError(
        423,
        { error: 'account_locked', message: '' },
        null,
        true,
      );
    if (action === 'login' && scenario === 'unverified')
      throw httpError(
        403,
        { error: 'email_unverified', message: '' },
        null,
        true,
      );
    if (action === 'login' && input.email === 'wrong@example.com')
      throw httpError(
        401,
        { error: 'invalid_credentials', message: '' },
        null,
        true,
      );
    if (
      (action === 'verify-email' || action === 'reset-password') &&
      input.token !== 'demo-token'
    )
      throw httpError(
        400,
        { error: 'invalid_or_expired_token', message: '' },
        null,
        true,
      );
  },
  async list(signal) {
    await wait(signal);
    return scenario === 'empty' ? [] : rows.map((row) => ({ ...row }));
  },
  async get(id, signal) {
    await wait(signal);
    return { ...find(id) };
  },
  async update(id, changes, signal) {
    await wait(signal);
    const next = { ...find(id), ...changes };
    rows = rows.map((row) => (row.linkId === id ? next : row));
    return { ...next };
  },
  async remove(id, signal) {
    await wait(signal);
    find(id);
    rows = rows.filter((row) => row.linkId !== id);
  },
  async analytics(id, days, signal) {
    await wait(signal);
    const row = find(id);
    const daily = Array.from({ length: days }, (_, i) => ({
      date: new Date(Date.UTC(2026, 9, 6 - days + i + 1))
        .toISOString()
        .slice(0, 10),
      clicks: row.clicks ? ((i * 13 + Number(id) * 7) % 37) + 4 : 0,
    }));
    const total = daily.reduce((sum, d) => sum + d.clicks, 0);
    const direct = Math.floor(total * 0.58);
    const social = Math.floor(total * 0.27);
    const mobile = Math.floor(total * 0.64);
    return {
      daily,
      updatedAt: '2026-10-06T09:00:00Z',
      referrers: [
        { name: 'Direct / unknown', clicks: direct },
        { name: 'Social', clicks: social },
        { name: 'Other websites', clicks: total - direct - social },
      ],
      devices: [
        { name: 'Mobile', clicks: mobile },
        { name: 'Desktop', clicks: total - mobile },
      ],
    };
  },
  async qr(link, signal) {
    await wait(signal);
    const qr = await import('qrcode');
    return qr.toDataURL(link.shortUrl, {
      width: 1024,
      margin: 4,
      errorCorrectionLevel: 'M',
    });
  },
};
