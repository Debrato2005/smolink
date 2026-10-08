import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.use({ timezoneId: 'Asia/Kolkata' });

test('calendar sets a local expiry and preserves the time when the date changes', async ({
  page,
}) => {
  await page.goto('/');
  await page.getByLabel('Set an expiry').check();
  await page.getByLabel('Expiry date and time').click();
  const calendar = page.getByRole('dialog', { name: 'Choose expiry date' });
  await expect(calendar).toBeVisible();
  await calendar.getByRole('button', { name: /next month/i }).click();
  await calendar
    .locator('button[data-day]')
    .filter({ hasText: /^15$/ })
    .click();
  const expiry = page.getByLabel('Expiry date and time');
  await expect(calendar.getByLabel('Time', { exact: true })).toHaveValue(
    '12:00',
  );
  await calendar.getByLabel('Time', { exact: true }).fill('18:30');
  await calendar
    .locator('button[data-day]')
    .filter({ hasText: /^16$/ })
    .click();
  await expect(calendar.getByLabel('Time', { exact: true })).toHaveValue(
    '18:30',
  );
  const date = await calendar.getByLabel('Date', { exact: true }).inputValue();
  expect(date).toMatch(/-16$/);
  const display = await page.evaluate(
    (value) =>
      new Date(value).toLocaleString('en', {
        dateStyle: 'medium',
        timeStyle: 'short',
      }),
    `${date}T18:30`,
  );
  await calendar.getByRole('button', { name: 'Done', exact: true }).click();
  await expect(expiry).toContainText(display);
  await page
    .getByLabel('Destination URL')
    .fill('https://example.com/calendar-check');
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  await expect(page.getByLabel('Short URL', { exact: true })).not.toHaveValue(
    '',
  );
  await expect(page.locator('.ticket-meta')).toContainText(display);
});

test('contact fields compose an email draft and do not report a sent message', async ({
  page,
}) => {
  await page.goto('/');
  await page
    .getByRole('button', { name: 'Contact me', exact: true })
    .first()
    .click();
  const dialog = page.getByRole('dialog', { name: 'Say hello.' });
  await expect(dialog).toBeVisible();
  await dialog.getByLabel('Name', { exact: true }).fill('Test visitor');
  await dialog.getByLabel('Email', { exact: true }).fill('visitor@example.com');
  await dialog
    .getByLabel('Message', { exact: true })
    .fill('A question about Smolink & expiry.');
  const draft = dialog.getByRole('link', { name: 'Open email draft' });
  const href = await draft.getAttribute('href');
  expect(href).toMatch(/^mailto:debrato2005@gmail\.com\?/);
  expect(decodeURIComponent(href!)).toContain(
    'A question about Smolink & expiry.',
  );
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.keyboard.press('Escape');
  await expect(dialog).toHaveCount(0);
  await expect(
    page.getByRole('button', { name: 'Contact me', exact: true }).first(),
  ).toBeFocused();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole('button', { name: 'Open navigation' }).click();
  const contact = page
    .getByRole('navigation', { name: 'Mobile navigation' })
    .getByRole('button', { name: 'Contact me' });
  await contact.click();
  await expect(dialog).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(contact).toBeFocused();
});

test('workspace controls filter links, keep URL state and collapse the sidebar', async ({
  page,
}) => {
  await page.goto('/login');
  await page.getByRole('button', { name: 'Use test account' }).click();
  await page.getByRole('combobox', { name: 'Status', exact: true }).click();
  await page.getByRole('option', { name: 'Paused', exact: true }).click();
  await expect(page).toHaveURL(/status=paused/);
  await expect(
    page.getByRole('link', { name: 'press-pack', exact: true }),
  ).toBeVisible();
  await page.getByRole('combobox', { name: 'Status', exact: true }).click();
  await page.getByRole('option', { name: 'All statuses', exact: true }).click();
  const sort = page.getByRole('combobox', { name: 'Sort by', exact: true });
  await sort.focus();
  await page.keyboard.press('ArrowDown');
  const search = page.getByRole('combobox', { name: 'Search sort by options' });
  await search.fill('clicks');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/sort=clicks/);
  await page.getByRole('button', { name: 'Collapse sidebar' }).click();
  const navigation = page.getByRole('navigation', {
    name: 'Workspace navigation',
  });
  await navigation.getByRole('link', { name: 'Overview', exact: true }).click();
  await expect(page).toHaveURL(/view=analytics/);
  await page.getByRole('button', { name: 'Expand sidebar' }).click();
  await expect(
    navigation.getByRole('link', { name: 'Overview', exact: true }),
  ).toHaveAttribute('aria-current', 'page');
});

test('shortening shows a skeleton while pending and a result only after completion', async ({
  page,
}) => {
  await page.clock.install();
  await page.goto('/');
  await page
    .getByLabel('Destination URL')
    .fill('https://example.com/loading-check');
  await page.clock.pauseAt(new Date(Date.now() + 1000));
  await page.getByRole('button', { name: 'Shorten URL' }).click();
  const pending = page.getByRole('status', { name: 'Creating your link…' });
  await expect(pending).toBeVisible();
  await expect(pending.locator('[data-slot="skeleton"]')).toHaveCount(2);
  await expect(
    page.getByRole('button', { name: 'Shortening…' }),
  ).toBeDisabled();
  await expect(page.getByLabel('Short URL', { exact: true })).toHaveCount(0);
  await page.clock.runFor(1000);
  await expect(page.getByLabel('Short URL', { exact: true })).not.toHaveValue(
    '',
  );
  await expect(pending).toHaveCount(0);
});

for (const width of [320, 1440]) {
  test(`QR loading reserves the preview and download space at ${width}px`, async ({
    page,
  }, testInfo) => {
    await page.setViewportSize({ width, height: 900 });
    await page.clock.install();
    await page.goto('/');
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: testInfo.outputPath('hero.png') });
    await page
      .getByLabel('Destination URL')
      .fill('https://example.com/qr-loading');
    await page.getByRole('button', { name: 'Shorten URL' }).click();
    await expect(page.getByLabel('Short URL', { exact: true })).not.toHaveValue(
      '',
    );
    await page.clock.pauseAt(new Date(Date.now() + 1000));
    await page.getByRole('button', { name: 'View QR code' }).click();
    const dialog = page.getByRole('dialog');
    const pending = dialog.getByRole('status', { name: 'Generating QR code…' });
    await expect(pending).toBeVisible();
    const skeleton = pending.locator('[data-slot="skeleton"]');
    await expect(skeleton).toHaveCount(1);
    const placeholder = (await skeleton.boundingBox())!;
    expect(placeholder.width).toBeGreaterThan(180);
    expect(Math.abs(placeholder.width - placeholder.height)).toBeLessThan(1);
    await expect(
      dialog.getByRole('button', { name: 'Download PNG' }),
    ).toBeDisabled();
    await expect(
      dialog.getByRole('link', { name: 'Download PNG' }),
    ).toHaveCount(0);
    const loadingBounds = (await dialog.boundingBox())!;
    await page.screenshot({ path: testInfo.outputPath('qr-pending.png') });
    await page.clock.runFor(1000);
    const preview = dialog.getByRole('img', {
      name: 'QR code for your short link',
    });
    await expect(preview).toBeVisible();
    await expect(preview).toHaveJSProperty('complete', true);
    const image = (await preview.boundingBox())!;
    expect(Math.abs(image.width - placeholder.width)).toBeLessThan(1);
    expect(Math.abs(image.height - placeholder.height)).toBeLessThan(1);
    const readyBounds = (await dialog.boundingBox())!;
    expect(Math.abs(readyBounds.height - loadingBounds.height)).toBeLessThan(1);
    await expect(pending).toHaveCount(0);
    await expect(
      dialog.getByRole('link', { name: 'Download PNG' }),
    ).toBeVisible();
    await page.screenshot({ path: testInfo.outputPath('qr-ready.png') });
    await page.clock.resume();
    await page.keyboard.press('Escape');
    await expect(dialog).toHaveCount(0);
    await expect(
      page.getByRole('button', { name: 'View QR code' }),
    ).toBeFocused();
  });
}

for (const width of [320, 901, 1440]) {
  test(`hero tickets and separator share symmetric alignment at ${width}px`, async ({
    page,
  }, testInfo) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('/');
    await page.evaluate(() => document.fonts.ready);
    const geometry = await page.evaluate(() => {
      const box = (element: Element) => {
        const r = element.getBoundingClientRect();
        return {
          x: r.x,
          y: r.y,
          width: r.width,
          height: r.height,
          centerX: r.x + r.width / 2,
          centerY: r.y + r.height / 2,
        };
      };
      const headline = document.querySelector('.hero .display')!;
      const range = document.createRange();
      range.selectNode(headline.firstChild!);
      const title = range.getBoundingClientRect();
      return {
        titleLeft: title.x,
        titleCenter: title.x + title.width / 2,
        highlight: box(document.querySelector('.hero-highlight')!),
        group: box(document.querySelector('.hero-link-illustration')!),
        scissors: box(document.querySelector('.hero-cut-line svg')!),
        arrow: box(document.querySelector('.hero-link-arrow')!),
        tickets: [...document.querySelectorAll('.hero-link-sticker')].map(
          (element) => {
            const css = getComputedStyle(element);
            return {
              ...box(element),
              label: box(element.querySelector('.hero-sticker-label')!),
              textFits:
                element.querySelector('.hero-sticker-text')!.scrollWidth <=
                element.clientWidth -
                  parseFloat(css.paddingLeft) -
                  parseFloat(css.paddingRight) +
                  1,
            };
          },
        ),
        overflow: document.documentElement.scrollWidth > innerWidth,
      };
    });
    expect(
      width > 900
        ? Math.abs(geometry.highlight.x - geometry.titleLeft)
        : Math.abs(geometry.highlight.centerX - geometry.titleCenter),
    ).toBeLessThan(1);
    expect(
      Math.abs(geometry.tickets[0]!.centerY - geometry.tickets[1]!.centerY),
    ).toBeLessThan(1);
    expect(
      Math.abs(geometry.tickets[0]!.height - geometry.tickets[1]!.height),
    ).toBeLessThan(1);
    for (const ticket of geometry.tickets) {
      expect(ticket.x).toBeGreaterThanOrEqual(0);
      expect(Math.abs(ticket.label.centerX - ticket.centerX)).toBeLessThan(1);
      expect(ticket.textFits).toBe(true);
    }
    expect(
      Math.abs(geometry.scissors.centerY - geometry.arrow.centerY),
    ).toBeLessThan(1);
    expect(
      Math.abs(geometry.scissors.centerX - geometry.group.centerX),
    ).toBeLessThan(1);
    expect(geometry.overflow).toBe(false);
    await page.screenshot({ path: testInfo.outputPath('hero-symmetric.png') });
  });
}

for (const width of [320, 768, 1051, 1440]) {
  test(`footer links, contact and layout work at ${width}px`, async ({
    page,
  }, testInfo) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('/#questions');
    const footer = page.locator('.site-footer');
    await footer.scrollIntoViewIfNeeded();
    expect((await footer.boundingBox())!.height).toBeLessThanOrEqual(
      width < 600 ? 400 : 260,
    );
    await expect(
      footer.getByRole('link', { name: 'Smolink home', exact: true }),
    ).toHaveAttribute('href', '/');
    await expect(
      footer.getByRole('link', { name: /Built by debrato/ }),
    ).toHaveAttribute('href', 'https://github.com/Debrato2005');
    const chai = footer.getByRole('link', { name: 'OnlyChai', exact: true });
    await expect(chai).toHaveAttribute(
      'href',
      'https://onlychai.neocities.org/support?name=debrato&upi=debrato2005%40oksbi',
    );
    await expect(chai).toHaveAttribute('target', '_blank');
    await expect(chai).toHaveAttribute('rel', 'noopener noreferrer');
    await expect(
      footer.getByRole('button', { name: 'Ko-fi (coming soon)', exact: true }),
    ).toBeDisabled();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth > innerWidth,
      ),
    ).toBe(false);
    await page.screenshot({ path: testInfo.outputPath('footer.png') });
    const contact = footer.getByRole('button', {
      name: 'Contact me',
      exact: true,
    });
    await contact.click();
    await expect(
      page.getByRole('dialog', { name: 'Say hello.' }),
    ).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(contact).toBeFocused();
    expect(
      (await new AxeBuilder({ page }).include('.site-footer').analyze())
        .violations,
    ).toEqual([]);
    await footer
      .getByRole('link', { name: 'Smolink home', exact: true })
      .click();
    await expect(page).toHaveURL(/\/$/);
  });
}
