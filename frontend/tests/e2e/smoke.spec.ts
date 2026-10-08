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
  await page.getByLabel('Destination URL').fill('https://example.com/reading');
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(
    page.getByText('Your link is ready', { exact: true }),
  ).toBeVisible();
  await expect(page.getByLabel('Short URL', { exact: true })).toHaveValue(
    /https:\/\/smolink\.test\/[a-z0-9]+$/,
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
  // main.tsx renders after an async gateway import, which can follow `load`.
  await page.getByRole('link', { name: 'Skip to content' }).waitFor({
    state: 'attached',
  });
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

test('home reload starts at the full hero after scrolling or following a section link', async ({
  page,
}) => {
  for (const [width, height] of [
    [1440, 900],
    [390, 844],
  ] as const) {
    await page.setViewportSize({ width, height });
    await page.goto('/');
    const hero = page.getByRole('heading', { level: 1 });
    await expect(hero).toBeVisible();
    await page
      .getByRole('heading', { name: 'Small links. Big features.' })
      .scrollIntoViewIfNeeded();
    expect(await page.evaluate(() => scrollY)).toBeGreaterThan(100);
    await page.reload();
    await expect(hero).toBeVisible();
    await expect.poll(() => page.evaluate(() => scrollY)).toBe(0);
    const header = (await page.locator('.site-header').boundingBox())!;
    expect((await hero.boundingBox())!.y).toBeGreaterThanOrEqual(header.height);

    await page.goto('/#questions');
    await expect(
      page.getByRole('heading', { name: 'Questions', exact: true }),
    ).toBeVisible();
    expect(await page.evaluate(() => scrollY)).toBeGreaterThan(100);
    await page.reload();
    await expect(hero).toBeVisible();
    await expect.poll(() => page.evaluate(() => scrollY)).toBe(0);
    await expect(page).toHaveURL(/\/$/);
    await page
      .locator('.site-footer')
      .getByRole('link', { name: 'Questions' })
      .click();
    await expect(page).toHaveURL(/\/#questions$/);
    expect(await page.evaluate(() => scrollY)).toBeGreaterThan(100);
  }
});

test('navbar social links remain usable when the star badge fails and on phones', async ({
  page,
}) => {
  await page.route('https://img.shields.io/**', (route) => route.abort());
  await page.goto('/');
  const header = page.locator('.site-header');
  const github = header.getByRole('link', { name: 'Star Smolink on GitHub' });
  const x = header.getByRole('link', { name: 'Debrato on X' });
  for (const [link, href] of [
    [github, 'https://github.com/Debrato2005/smolink'],
    [x, 'https://x.com/DebratoG'],
  ] as const) {
    await expect(link).toBeVisible();
    await expect(link).toHaveAttribute('href', href);
    await expect(link).toHaveAttribute('target', '_blank');
    await expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    await link.focus();
    await expect(link).toBeFocused();
  }
  await expect(github).toContainText('Star');
  await page.setViewportSize({ width: 1051, height: 900 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.setViewportSize({ width: 320, height: 900 });
  await page.getByRole('button', { name: 'Open navigation' }).click();
  const mobile = page.getByRole('navigation', { name: 'Mobile navigation' });
  await expect(
    mobile.getByRole('link', { name: 'Star Smolink on GitHub' }),
  ).toBeVisible();
  await expect(
    mobile.getByRole('link', { name: 'Debrato on X' }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});

test('navbar items box on hover, focus and the active route, then collapse on phones', async ({
  page,
}) => {
  const boxed = (locator: import('@playwright/test').Locator) =>
    locator.evaluate((element) => {
      const style = getComputedStyle(element);
      return {
        fill: style.backgroundColor,
        shadow: style.boxShadow,
        moved: style.transform !== 'none',
        duration: style.transitionDuration,
      };
    });
  await page.setViewportSize({ width: 1440, height: 800 });
  await page.goto('/');
  const navigation = page.getByRole('navigation', { name: 'Main navigation' });
  const item = navigation.getByRole('link', { name: 'Questions' });
  const rest = await boxed(item);
  expect(rest.shadow).toBe('none');
  expect(rest.moved).toBe(false);
  // Every transition is quick and tactile: between 120 and 180 ms.
  for (const part of rest.duration.split(','))
    expect(parseFloat(part) * 1000).toBeGreaterThanOrEqual(120);
  for (const part of rest.duration.split(','))
    expect(parseFloat(part) * 1000).toBeLessThanOrEqual(180);
  await item.hover();
  await expect
    .poll(async () => (await boxed(item)).shadow)
    .toBe('rgb(0, 0, 0) 4px 4px 0px 0px');
  expect((await boxed(item)).moved).toBe(true);
  await page.mouse.move(0, 700);
  await item.focus();
  await expect
    .poll(async () => (await boxed(item)).shadow)
    .toContain('4px 4px 0px 0px');
  await page.goto('/dashboard');
  const active = navigation.getByRole('link', { name: 'Workspace' });
  await expect(active).toHaveAttribute('aria-current', 'page');
  await expect
    .poll(async () => (await boxed(active)).shadow)
    .toContain('4px 4px 0px 0px');
  await page.emulateMedia({ reducedMotion: 'reduce' });
  expect((await boxed(active)).moved).toBe(false);
  for (const width of [1024, 768, 390]) {
    await page.setViewportSize({ width, height: 800 });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await expect(navigation).not.toBeVisible();
    await expect(
      page.getByRole('button', { name: 'Open navigation' }),
    ).toBeVisible();
  }
});

test('boxed blocks lift on hover without changing layout and respect reduced motion', async ({
  page,
  browser,
}) => {
  test.slow();
  const checkBlocks = async (selector: string) => {
    const blocks = page.locator(selector);
    expect(await blocks.count()).toBeGreaterThan(0);
    for (const block of await blocks.all()) {
      const lift = await block.evaluate((el) =>
        el.matches('.feature-card, .step-list li, .faq-list details') ? 6 : 2,
      );
      await page.mouse.move(0, 0);
      await block.scrollIntoViewIfNeeded();
      await expect
        .poll(() => block.evaluate((el) => getComputedStyle(el).transform))
        .toBe('none');
      const before = await block.boundingBox();
      const shadow = await block.evaluate(
        (el) => getComputedStyle(el).boxShadow,
      );
      await block.hover();
      await expect
        .poll(() => block.evaluate((el) => getComputedStyle(el).transform))
        .toBe(`matrix(1, 0, 0, 1, -${lift}, -${lift})`);
      const after = await block.boundingBox();
      expect(after!.width).toBe(before!.width);
      expect(after!.height).toBe(before!.height);
      expect(after!.x).toBeCloseTo(before!.x - lift);
      expect(after!.y).toBeCloseTo(before!.y - lift);
      expect(
        await block.evaluate((el) => getComputedStyle(el).boxShadow),
      ).not.toBe(shadow);
      await page.emulateMedia({ reducedMotion: 'reduce' });
      expect(await block.evaluate((el) => getComputedStyle(el).transform)).toBe(
        'none',
      );
      expect(
        await block.evaluate((el) => getComputedStyle(el).transitionDuration),
      ).toBe('0s');
      await page.mouse.move(0, 0);
      await page.emulateMedia({ reducedMotion: 'no-preference' });
    }
  };
  await page.goto('/');
  await page.getByLabel('Destination URL').waitFor();
  const bench = page.locator('.hero .bench');
  const shadow = await bench.evaluate((el) => getComputedStyle(el).boxShadow);
  await bench.hover();
  await expect
    .poll(() => bench.evaluate((el) => getComputedStyle(el).transform))
    .toBe('none');
  await expect
    .poll(() => bench.evaluate((el) => getComputedStyle(el).boxShadow))
    .toBe(shadow);
  await checkBlocks('.feature-card, .step-list li, .faq-list details');
  await page.goto('/login');
  await page.getByRole('button', { name: 'Use test account' }).waitFor();
  await checkBlocks('.auth-poster, .auth-content');
  await page.getByRole('button', { name: 'Use test account' }).click();
  await page.getByLabel('Search links').waitFor();
  await checkBlocks('.ledger, .links-panel');
  await page.getByRole('link', { name: 'portfolio', exact: true }).click();
  await page.getByRole('button', { name: 'Save changes' }).waitFor();
  await checkBlocks('.ticket, .edit-form, .detail-meta, .danger-zone');
  await page.getByRole('link', { name: 'View analytics' }).click();
  await page.getByRole('table', { name: 'Daily clicks' }).waitFor();
  await checkBlocks('.chart-panel, .breakdown, .daily-data');
  const touchPage = await browser.newPage({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true,
  });
  await touchPage.goto(new URL('/', page.url()).href);
  const touchCard = touchPage.getByRole('article').first();
  await touchCard.hover();
  expect(await touchCard.evaluate((el) => getComputedStyle(el).transform)).toBe(
    'none',
  );
  await touchPage.close();
});
