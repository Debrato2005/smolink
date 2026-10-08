import { expect, test } from '@playwright/test';

test('production uses live transport and presents failure without a fixture fallback', async ({
  page,
}) => {
  const errors: string[] = [];
  const requests: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  // Failure injection exercises the shipped client; it is not backend evidence.
  await page.route('**/api/v1/urls', async (route) => {
    requests.push(route.request().method());
    await route.fulfill({
      status: 503,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'private server diagnostic' }),
    });
  });
  await page.goto('/');
  // Production copy never presents the product as a demo or sample.
  expect(await page.locator('body').innerText()).not.toMatch(
    /\b(demo|sample|synthetic|fixture)\b/i,
  );
  await page
    .getByLabel('Destination URL')
    .fill('https://example.com/production');
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(page.getByRole('alert')).toContainText(
    'The service is unavailable.',
  );
  await expect(page.getByRole('alert')).toContainText('may have been created');
  await expect(page.getByLabel('Short URL')).toHaveCount(0);
  await expect(page.getByText('private server diagnostic')).toHaveCount(0);
  expect(requests).toEqual(['POST']);
  expect(errors).toEqual([]);
  expect(
    await page.evaluate(() => localStorage.length + sessionStorage.length),
  ).toBe(0);
});

test('email credentials are removed for every router-equivalent email path', async ({
  page,
}) => {
  for (const [path, title] of [
    ['/verify-email', 'Verify your email'],
    ['/verify-email/', 'Verify your email'],
    ['/VERIFY-EMAIL', 'Verify your email'],
    ['/%76erify-email', 'Verify your email'],
    ['/reset-password/', 'Choose a new password'],
  ]) {
    await page.goto(`${path}#token=secret-example`);
    await expect(page.getByRole('heading', { level: 1 })).toHaveText(title!);
    await expect.poll(() => page.evaluate(() => window.location.hash)).toBe('');
  }
});

test('production sends normalized alias and timezone-aware expiry, handles conflicts, and preserves uncertain results', async ({
  page,
}) => {
  const bodies: Record<string, unknown>[] = [];
  let status = 409;
  await page.route('**/api/v1/urls', async (route) => {
    bodies.push(route.request().postDataJSON() as Record<string, unknown>);
    await route.fulfill({
      status,
      contentType: 'application/json',
      body:
        status === 409
          ? JSON.stringify({
              error: 'alias_taken',
              message: 'private diagnostic',
            })
          : status === 429
            ? JSON.stringify({ detail: 'limited' })
            : '<invalid-success>',
      headers: status === 429 ? { 'Retry-After': '17' } : {},
    });
  });
  await page.goto('/');
  await page.getByLabel('Destination URL').fill('https://example.com/wire');
  await page.getByLabel('Custom alias').fill('My-Link');
  await page.getByLabel('Set an expiry').check();
  await page.getByLabel('Expiry date and time').click();
  await page.getByLabel('Date', { exact: true }).fill('2030-07-20');
  await page.getByLabel('Time', { exact: true }).fill('15:30');
  await page.getByRole('button', { name: 'Done', exact: true }).click();
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(page.getByRole('alert')).toContainText('alias is taken');
  expect(bodies[0]?.alias).toBe('my-link');
  expect(bodies[0]?.expires_at).toBe(
    await page.evaluate(() => new Date('2030-07-20T15:30').toISOString()),
  );
  status = 429;
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(page.getByRole('alert')).toContainText('Wait 17 seconds.');
  status = 201;
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(page.getByRole('alert')).toContainText('may have been created');
  await expect(page.getByLabel('Short URL', { exact: true })).toHaveCount(0);
  await expect(page.getByLabel('Destination URL')).toHaveValue(
    'https://example.com/wire',
  );
  expect(bodies).toHaveLength(3);
});

test('production success uses returned public URL while account and QR gaps remain explicit', async ({
  page,
}) => {
  const calls: string[] = [];
  page.on('request', (request) => {
    if (request.url().includes('/api/v1')) calls.push(request.url());
  });
  await page.route('**/api/v1/urls', (route) =>
    route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 7440000000000000000,
        short_code: 'created',
        short_url: 'https://short.example/created',
        destination: 'https://example.com/',
        created_at: '2026-10-06T09:00:00Z',
        expires_at: null,
      }),
    }),
  );
  await page.goto('/');
  await page.getByLabel('Destination URL').fill('https://example.com');
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(page.getByLabel('Short URL', { exact: true })).toHaveValue(
    'https://short.example/created',
  );
  await expect(
    page.getByRole('button', { name: 'View QR code' }),
  ).toBeDisabled();
  await page.getByRole('link', { name: 'Sign in', exact: true }).click();
  await expect(
    page.getByRole('button', { name: 'Sign in', exact: true }),
  ).toBeDisabled();
  await expect(
    page.getByRole('button', { name: 'Use test account' }),
  ).toHaveCount(0);
  await expect(
    page.getByRole('button', { name: 'Continue with Google' }),
  ).toBeDisabled();
  await expect(page.getByText('Accounts are coming soon.')).toBeVisible();
  await page.goto('/dashboard');
  await expect(
    page.getByRole('heading', { name: 'Your workspace is on its way.' }),
  ).toBeVisible();
  expect(calls).toHaveLength(1);
});
