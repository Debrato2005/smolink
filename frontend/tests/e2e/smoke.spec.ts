import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('guest preview and account navigation have no API calls or browser errors', async ({
  page,
}) => {
  const errors: string[] = [];
  const requests: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push(m.text());
  });
  page.on('request', (r) => {
    if (r.url().includes('/api/v1')) requests.push(r.url());
  });
  await page.goto('/');
  await expect(page.getByText('Demo mode', { exact: true })).toBeVisible();
  await page.getByLabel('Destination URL').fill('https://example.com/reading');
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(
    page.getByText('Demo link ready', { exact: true }),
  ).toBeVisible();
  await expect(page.getByLabel('Short URL', { exact: true })).toHaveValue(
    /https:\/\/smolink.invalid\/demo-\d+/,
  );
  await page.getByRole('link', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('main')).toBeFocused();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Sign in');
  await page.reload();
  await expect(page.getByLabel('Email address')).toBeVisible();
  expect(errors).toEqual([]);
  expect(requests).toEqual([]);
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
        .analyze()
    ).violations,
  ).toEqual([]);
});
for (const width of [320, 390, 768, 1024, 1440]) {
  test(`home reflows and passes axe at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('/');
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
    await page.screenshot({
      path: `test-results/${test.info().project.name}-${width}.png`,
    });
  });
}
test('keyboard, navigation recovery, resize and reduced motion remain usable', async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  await page.keyboard.press('Tab');
  await expect(
    page.getByRole('link', { name: 'Skip to content' }),
  ).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('main')).toBeFocused();
  const button = page.getByRole('button', { name: 'Shorten URL' });
  expect(
    await button.evaluate((el) => getComputedStyle(el).transitionDuration),
  ).toBe('0s');
  await button.hover();
  expect(await button.evaluate((el) => getComputedStyle(el).transform)).toBe(
    'none',
  );
  await page.getByLabel('Destination URL').fill('https://example.com/resize');
  for (const width of [390, 1440, 320]) {
    await page.setViewportSize({ width, height: 900 });
    await expect(page.getByLabel('Destination URL')).toHaveValue(
      'https://example.com/resize',
    );
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
  }
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(
    'A home for your links.',
  );
  await page.goto('/missing');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(
    'Page not found',
  );
  await page.getByRole('link', { name: 'Back to short links' }).click();
  await expect(page.getByLabel('Destination URL')).toBeVisible();
});
