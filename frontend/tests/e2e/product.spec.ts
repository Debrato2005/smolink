import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('guest customizes a link, recovers validation, copies and downloads a real QR', async ({
  page,
}) => {
  await page.goto('/');
  await page.getByLabel('Destination URL').fill('https://example.com/launch');
  await page.getByLabel('Custom alias').fill('a!');
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(
    page.getByText('Use 3–64 letters, numbers, or hyphens.'),
  ).toBeVisible();
  await page.getByLabel('Custom alias').fill('launch-kit');
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(page.getByLabel('Short URL', { exact: true })).toHaveValue(
    'https://smolink.invalid/launch-kit',
  );
  await page.getByRole('button', { name: 'View QR code' }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(
    page.getByRole('img', { name: 'QR code for your short link' }),
  ).toBeVisible();
  const download = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Download PNG' }).click();
  expect((await download).suggestedFilename()).toBe('smolink-launch-kit.png');
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await expect(
    page.getByRole('button', { name: 'View QR code' }),
  ).toBeFocused();
});

test('demo workspace supports search, management, analytics and confirmed deletion', async ({
  page,
}) => {
  await page.goto('/login');
  await page.getByRole('button', { name: 'Explore demo workspace' }).click();
  await expect(
    page.getByRole('heading', { name: 'Your links', exact: true }),
  ).toBeVisible();
  await page.getByLabel('Search links').fill('portfolio');
  await expect(
    page.getByRole('link', { name: 'portfolio', exact: true }),
  ).toBeVisible();
  await page.getByRole('link', { name: 'portfolio', exact: true }).click();
  await expect(
    page.getByRole('heading', { name: 'Link details' }),
  ).toBeVisible();
  await page.getByRole('link', { name: 'View analytics' }).click();
  await expect(
    page.getByRole('heading', { name: 'Link analytics' }),
  ).toBeVisible();
  await expect(page.getByRole('table', { name: 'Daily clicks' })).toBeVisible();
  await page.getByRole('link', { name: 'Link details', exact: true }).click();
  await page.getByRole('button', { name: 'Delete link', exact: true }).click();
  await page.getByRole('button', { name: 'Cancel', exact: true }).click();
  await expect(
    page.getByRole('heading', { name: 'Link details' }),
  ).toBeVisible();
  await page.getByRole('button', { name: 'Delete link', exact: true }).click();
  await page
    .getByRole('dialog')
    .getByRole('button', { name: 'Delete link', exact: true })
    .click();
  await expect(
    page.getByRole('heading', { name: 'Your links', exact: true }),
  ).toBeVisible();
  await page.getByLabel('Search links').fill('portfolio');
  await expect(
    page.getByRole('heading', { name: 'No matching links' }),
  ).toBeVisible();
});

test('expiry validation, alias conflict and service errors preserve the entered URL', async ({
  page,
}) => {
  await page.goto('/');
  await page.getByLabel('Destination URL').fill('javascript:alert(1)');
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(
    page.getByText(
      'Enter a complete http:// or https:// URL without credentials.',
    ),
  ).toBeVisible();
  await page.getByLabel('Destination URL').fill('https://example.com/keep-me');
  await page.getByLabel('Custom alias').fill('portfolio');
  await page.getByLabel('Set an expiry').check();
  await page.getByLabel('Expiry date and time').fill('2020-01-01T12:00');
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(page.getByText('Choose a future expiry time.')).toBeVisible();
  await page.getByLabel('Set an expiry').uncheck();
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(page.getByRole('alert')).toContainText('This alias is taken');
  await expect(page.getByLabel('Custom alias')).toHaveAttribute(
    'aria-invalid',
    'true',
  );
  await page.getByText('Demo controls', { exact: true }).click();
  await page.getByLabel('Preview a state').selectOption('limited');
  await page.getByLabel('Custom alias').fill('my-valid-alias');
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(page.getByRole('alert')).toContainText('Wait 5 seconds.');
  await expect(page.getByLabel('Destination URL')).toHaveValue(
    'https://example.com/keep-me',
  );
  await page.getByLabel('Preview a state').selectOption('normal');
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(
    page.getByText('Demo link ready', { exact: true }),
  ).toBeVisible();
});

test('clipboard denial gives a selectable fallback and success awaits the clipboard', async ({
  page,
}) => {
  await page.goto('/');
  await page.getByLabel('Destination URL').fill('https://example.com/copy');
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(
    page.getByText('Demo link ready', { exact: true }),
  ).toBeVisible();
  await page.evaluate(() => {
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {
        writeText: async () => {
          throw new Error('denied');
        },
      },
    });
  });
  await page.getByRole('button', { name: 'Copy link', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText(
    'Clipboard access was denied',
  );
  const fallback = page.getByLabel(/Copy demo-\d+ manually/);
  await fallback.focus();
  expect(
    await fallback.evaluate(
      (el: HTMLInputElement) => el.selectionEnd! - el.selectionStart!,
    ),
  ).toBe((await fallback.inputValue()).length);
  await page.evaluate(() => {
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {
        writeText: async (value: string) => {
          document.documentElement.dataset.copiedValue = value;
        },
      },
    });
  });
  await page.getByRole('button', { name: 'Copy link', exact: true }).click();
  await expect(
    page.getByRole('button', { name: 'Copied', exact: true }),
  ).toBeVisible();
  expect(
    await page.evaluate(() => document.documentElement.dataset.copiedValue),
  ).toBe(await page.getByLabel('Short URL', { exact: true }).inputValue());
});

test('account forms cover registration, verification, recovery, reset and locked sign-in', async ({
  page,
}) => {
  await page.goto('/register');
  await page.getByLabel('Email address').fill('demo@example.com');
  await page.getByLabel('Password', { exact: true }).fill('short');
  await page
    .getByRole('button', { name: 'Create account', exact: true })
    .click();
  await expect(
    page.getByText('Use 12–128 characters for your password.'),
  ).toBeVisible();
  await page.getByLabel('Password', { exact: true }).fill('a-demo-password');
  await page
    .getByRole('button', { name: 'Create account', exact: true })
    .click();
  await expect(
    page.getByRole('heading', { name: 'Check your inbox' }),
  ).toBeVisible();
  await page.getByRole('link', { name: 'Preview verification' }).click();
  await page.getByRole('button', { name: 'Load demo email link' }).click();
  await page.getByRole('button', { name: 'Verify email', exact: true }).click();
  await expect(
    page.getByRole('heading', { name: 'Email verified', exact: true }),
  ).toBeVisible();
  await page.goto('/forgot-password');
  await page.getByLabel('Email address').fill('demo@example.com');
  await page.getByRole('button', { name: 'Send reset link' }).click();
  await expect(
    page.getByRole('heading', { name: 'Check your inbox' }),
  ).toBeVisible();
  await page.getByRole('link', { name: 'Preview password reset' }).click();
  await page.getByRole('button', { name: 'Load demo email link' }).click();
  await page.getByLabel('New password').fill('replacement-demo-password');
  await page
    .getByRole('button', { name: 'Reset password', exact: true })
    .click();
  await expect(
    page.getByRole('heading', { name: 'Password reset', exact: true }),
  ).toBeVisible();
  await page.goto('/login');
  await page.getByText('Demo controls', { exact: true }).click();
  await page.getByLabel('Preview a state').selectOption('locked');
  await page.getByLabel('Email address').fill('demo@example.com');
  await page.getByLabel('Password', { exact: true }).fill('sample-password');
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('temporarily locked');
  await page.getByLabel('Preview a state').selectOption('unverified');
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(
    page.getByRole('link', { name: 'Request a verification email' }),
  ).toBeVisible();
  await page.getByLabel('Preview a state').selectOption('normal');
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Your links' })).toBeVisible();
  expect(
    await page.evaluate(() => localStorage.length + sessionStorage.length),
  ).toBe(0);
  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(
    page.getByRole('heading', { name: 'Sign in', exact: true }),
  ).toBeVisible();
  await page.goto('/dashboard');
  await expect(
    page.getByRole('heading', { name: 'A home for your links.' }),
  ).toBeVisible();
});

test('workspace filters, pagination, edits and outages remain distinct from empty data', async ({
  page,
}) => {
  await page.goto('/login');
  await page.getByRole('button', { name: 'Explore demo workspace' }).click();
  await page.getByRole('button', { name: 'Next page' }).click();
  await expect(page).toHaveURL(/page=2/);
  await expect(
    page.getByRole('link', { name: 'project-notes', exact: true }),
  ).toBeVisible();
  await page.getByLabel('Status', { exact: true }).selectOption('paused');
  await expect(
    page.getByRole('link', { name: 'press-pack', exact: true }),
  ).toBeVisible();
  await expect(page).not.toHaveURL(/page=2/);
  await page.getByLabel('Status', { exact: true }).selectOption('all');
  await page.getByLabel('Sort by').selectOption('oldest');
  await expect(
    page.getByRole('link', { name: 'project-notes', exact: true }),
  ).toBeVisible();
  await page.getByRole('link', { name: 'project-notes', exact: true }).click();
  await page.getByLabel('Destination URL').fill('https://example.com/changed');
  await page.getByLabel('Link enabled').uncheck();
  await page.getByRole('button', { name: 'Save changes' }).click();
  await expect(
    page.getByRole('status').filter({ hasText: 'Demo changes saved' }),
  ).toBeVisible();
  await expect(page.getByLabel('Destination URL')).toHaveValue(
    'https://example.com/changed',
  );
  await page
    .getByRole('link', { name: 'All links', exact: true })
    .last()
    .click();
  await page.getByText('Demo controls', { exact: true }).click();
  await page.getByLabel('Preview a state').selectOption('error');
  await expect(page.getByRole('alert')).toContainText('unavailable');
  await expect(page.getByText('Total links', { exact: true })).toHaveCount(0);
  await page.getByLabel('Preview a state').selectOption('empty');
  await expect(
    page.getByRole('heading', {
      name: 'A little empty. A lot of possibility.',
    }),
  ).toBeVisible();
  await page.getByLabel('Preview a state').selectOption('expired');
  await expect(page.getByRole('link', { name: 'Sign in again' })).toBeVisible();
});

for (const width of [320, 768, 1440]) {
  test(`workspace and analytics reflow, text spacing and axe at ${width}px`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('/login');
    await page.getByRole('button', { name: 'Explore demo workspace' }).click();
    await page.getByLabel('Search links').waitFor();
    for (const route of ['dashboard', 'detail', 'analytics']) {
      if (route === 'detail')
        await page
          .getByRole('link', { name: 'portfolio', exact: true })
          .click();
      if (route === 'analytics')
        await page.getByRole('link', { name: 'View analytics' }).click();
      if (route === 'detail')
        await page.getByRole('button', { name: 'Save changes' }).waitFor();
      if (route === 'analytics')
        await page.getByRole('table', { name: 'Daily clicks' }).waitFor();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
      expect(
        (
          await new AxeBuilder({ page })
            .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
            .analyze()
        ).violations,
      ).toEqual([]);
      if (route === 'analytics') {
        const dailyData = page.getByRole('region', {
          name: 'Daily clicks data',
        });
        await dailyData.focus();
        await expect(dailyData).toBeFocused();
        await page.keyboard.press('ArrowDown');
        await expect
          .poll(() => dailyData.evaluate((element) => element.scrollTop))
          .toBeGreaterThan(0);
      }
      const spacing = await page.addStyleTag({
        content:
          '* { line-height: 1.5 !important; letter-spacing: .12em !important; word-spacing: .16em !important; } p { margin-bottom: 2em !important; }',
      });
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
      await spacing.evaluate((element) => (element as HTMLElement).remove());
    }
    await page.addStyleTag({
      content:
        '* { line-height: 1.5 !important; letter-spacing: .12em !important; word-spacing: .16em !important; } p { margin-bottom: 2em !important; }',
    });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
  });
}

test('workspace navigation preserves the creation task after sign-in and marks the current section', async ({
  page,
}) => {
  await page.goto('/dashboard/new');
  await page.getByRole('link', { name: 'Sign in', exact: true }).last().click();
  await page.getByRole('button', { name: 'Explore demo workspace' }).click();
  await expect(
    page.getByRole('heading', { name: 'Create a link', exact: true }),
  ).toBeVisible();
  const navigation = page.getByRole('navigation', {
    name: 'Workspace navigation',
  });
  await expect(
    navigation.getByRole('link', { name: 'Create a link' }),
  ).toHaveAttribute('aria-current', 'page');
  await navigation.getByRole('link', { name: 'All links' }).click();
  await page.getByRole('link', { name: 'portfolio', exact: true }).click();
  await expect(
    navigation.getByRole('link', { name: 'All links' }),
  ).toHaveAttribute('aria-current', 'page');
  await page.getByRole('link', { name: 'View analytics' }).click();
  await expect(
    navigation.getByRole('link', { name: 'Overview' }),
  ).toHaveAttribute('aria-current', 'page');
  await page.goto('/login?next=https%3A%2F%2Fexample.com');
  await page.getByRole('button', { name: 'Explore demo workspace' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
});

test('mobile navigation closes with Escape and restores focus', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await page.getByRole('button', { name: 'Open navigation' }).click();
  const navigation = page.getByRole('navigation', {
    name: 'Mobile navigation',
  });
  await navigation.getByRole('link', { name: 'How it works' }).focus();
  await page.keyboard.press('Escape');
  await expect(navigation).toHaveCount(0);
  await expect(
    page.getByRole('button', { name: 'Open navigation' }),
  ).toBeFocused();
});

test('narrow workspace supports long links, future expiry, QR and confirmed zero analytics', async ({
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 900 });
  await page.goto('/login');
  await page.getByRole('button', { name: 'Explore demo workspace' }).click();
  await page.getByRole('link', { name: 'Create link', exact: true }).click();
  const alias = 'a'.repeat(64);
  await page
    .getByLabel('Destination URL')
    .fill(`https://example.com/${'long-path/'.repeat(40)}`);
  await page.getByLabel('Custom alias').fill(alias);
  await page.getByLabel('Set an expiry').check();
  const future = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 16);
  await page.getByLabel('Expiry date and time').fill(future);
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(
    page.getByText('Demo link ready', { exact: true }),
  ).toBeVisible();
  await page.getByRole('link', { name: 'Back to all links' }).click();
  await page.getByLabel('Search links').fill(alias);
  await page.getByRole('link', { name: alias, exact: true }).click();
  await page.getByRole('button', { name: 'Save changes' }).waitFor();
  await expect(page.getByLabel('Expiry date and time')).not.toHaveValue('');
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.getByRole('button', { name: 'View QR code' }).click();
  await expect(
    page.getByRole('img', { name: 'QR code for your short link' }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.keyboard.press('Escape');
  await page.getByRole('link', { name: 'View analytics' }).click();
  await page.getByLabel('Date range').selectOption('30');
  await expect(
    page.getByText(
      'No sample clicks in this range. Zero is confirmed for this demo link.',
    ),
  ).toBeVisible();
  expect(
    await page
      .getByRole('table', { name: 'Daily clicks' })
      .locator('tbody tr')
      .count(),
  ).toBe(30);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});
