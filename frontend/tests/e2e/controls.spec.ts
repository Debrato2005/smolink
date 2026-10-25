import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.use({ timezoneId: 'Asia/Kolkata' });

for (const width of [320, 901, 1051, 1440]) {
  test(`account poster stays balanced and within the page at ${width}px`, async ({
    page,
  }, testInfo) => {
    await page.setViewportSize({ width, height: 900 });
    for (const path of ['/login', '/register']) {
      await page.goto(path);
      const form = page.locator('.auth-content');
      await expect(
        form.getByRole('button', { name: 'Continue with Google' }),
      ).toBeEnabled();
      const poster = page.locator('.auth-poster');
      if (width > 860) {
        const card = (await poster.boundingBox())!;
        const content = (await form.boundingBox())!;
        // Firefox can report fractional float noise around an integer CSS size.
        const height = Math.round(card.height * 100) / 100;
        expect(height).toBeGreaterThanOrEqual(500);
        expect(height).toBeLessThanOrEqual(600);
        expect(Math.abs(card.width - content.width)).toBeLessThan(1);
        expect(
          Math.abs(card.y + card.height / 2 - content.y - content.height / 2),
        ).toBeLessThan(1);
        const rows = await poster
          .locator('.poster-stubs span')
          .evaluateAll((elements) =>
            elements.map((element) => {
              const rect = element.getBoundingClientRect();
              return {
                x: rect.x,
                width: rect.width,
                fits: element.scrollWidth <= element.clientWidth,
              };
            }),
          );
        for (const row of rows) {
          expect(Math.abs(row.x - rows[0]!.x)).toBeLessThan(1);
          expect(Math.abs(row.width - rows[0]!.width)).toBeLessThan(1);
          expect(row.fits).toBe(true);
        }
      } else {
        await expect(poster).toBeHidden();
        const content = (await form.boundingBox())!;
        expect(
          Math.abs(content.x + content.width / 2 - width / 2),
        ).toBeLessThan(1);
      }
      if (width <= 560) {
        const accountAction = form.locator('.auth-switch a');
        expect(
          await accountAction.evaluate((element) => {
            const range = document.createRange();
            range.selectNodeContents(element);
            return [...range.getClientRects()].filter(
              (rect) => rect.width > 0 && rect.height > 0,
            ).length;
          }),
        ).toBe(1);
        expect(
          (await accountAction.boundingBox())!.height,
        ).toBeGreaterThanOrEqual(44);
      }
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth > innerWidth,
        ),
      ).toBe(false);
      expect(
        (await new AxeBuilder({ page }).include('.auth-layout').analyze())
          .violations,
      ).toEqual([]);
      await page.screenshot({
        path: testInfo.outputPath(`${path.slice(1)}.png`),
      });
    }
  });
}

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

test('phone calendar separates readable date and time fields and keeps Done reachable', async ({
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 600 });
  await page.goto('/');
  await page.getByLabel('Set an expiry').check();
  const expiry = page.getByLabel('Expiry date and time');
  await expiry.click();
  const calendar = page.getByRole('dialog', { name: 'Choose expiry date' });
  await calendar.getByRole('button', { name: /next month/i }).waitFor();
  await page.evaluate(() => document.fonts.ready);
  const date = calendar.getByLabel('Date', { exact: true });
  const time = calendar.getByLabel('Time', { exact: true });
  const popup = await calendar.evaluate((element) => {
    const bounds = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    return {
      left: bounds.left,
      right: bounds.right,
      contentWidth:
        element.clientWidth -
        parseFloat(style.paddingLeft) -
        parseFloat(style.paddingRight),
      fits: element.scrollWidth <= element.clientWidth + 1,
    };
  });
  const dateBounds = (await date.boundingBox())!;
  const timeBounds = (await time.boundingBox())!;
  expect(
    timeBounds.y - dateBounds.y - dateBounds.height,
  ).toBeGreaterThanOrEqual(11.5);
  for (const field of [date, time]) {
    expect((await field.boundingBox())!.width).toBeGreaterThanOrEqual(
      popup.contentWidth - 1,
    );
    expect(
      await field.evaluate((element) =>
        parseFloat(getComputedStyle(element).fontSize),
      ),
    ).toBeGreaterThanOrEqual(16);
  }
  expect(popup.left).toBeGreaterThanOrEqual(-1);
  expect(popup.right).toBeLessThanOrEqual(321);
  expect(popup.fits).toBe(true);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  const future = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10);
  await date.fill(future);
  await time.fill('18:30');
  const done = calendar.getByRole('button', { name: 'Done', exact: true });
  await done.scrollIntoViewIfNeeded();
  await expect(done).toBeInViewport({ ratio: 1 });
  await done.click();
  await expect(calendar).toBeHidden();
  await expect(expiry).toBeFocused();
  const display = await page.evaluate(
    (value) =>
      new Date(value).toLocaleString('en', {
        dateStyle: 'medium',
        timeStyle: 'short',
      }),
    `${future}T18:30`,
  );
  await expect(expiry).toContainText(display);
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

test('wide workspace fills the available width for links and analytics', async ({
  page,
}, testInfo) => {
  await page.goto('/login');
  await page.getByRole('button', { name: 'Use test account' }).click();
  const navigation = page.getByRole('navigation', {
    name: 'Workspace navigation',
  });
  for (const width of [1920, 2560]) {
    await page.setViewportSize({ width, height: 1080 });
    for (const collapsed of [false, true]) {
      if (collapsed)
        await page.getByRole('button', { name: 'Collapse sidebar' }).click();
      await navigation
        .getByRole('link', { name: 'All links', exact: true })
        .click();
      await expect(
        page.getByRole('link', { name: 'portfolio', exact: true }),
      ).toBeVisible();
      const content = page.locator('.workspace-content');
      const bounds = (await content.boundingBox())!;
      expect(bounds.x + bounds.width).toBeCloseTo(width, 0);
      await page.screenshot({
        path: testInfo.outputPath(
          `links-${width}-${collapsed ? 'collapsed' : 'expanded'}.png`,
        ),
      });
      await navigation
        .getByRole('link', { name: 'Create a link', exact: true })
        .click();
      const bench = page.locator('.workspace-create .bench');
      await expect(bench).toBeVisible();
      expect(
        await bench.evaluate((element) => {
          const content = element.closest('.workspace-content')!;
          return Math.abs(
            element.getBoundingClientRect().right -
              content.getBoundingClientRect().right +
              parseFloat(getComputedStyle(content).paddingRight),
          );
        }),
      ).toBeLessThan(1);
      await page
        .getByLabel('Destination URL')
        .fill('https://example.com/workspace-width');
      await page
        .getByLabel('Custom alias')
        .fill(`width-${width}-${collapsed ? 'collapsed' : 'expanded'}`);
      await page.getByRole('button', { name: 'Shorten URL' }).click();
      await expect(
        page.getByText('Your link is ready', { exact: true }),
      ).toBeVisible();
      await page.screenshot({
        path: testInfo.outputPath(
          `create-${width}-${collapsed ? 'collapsed' : 'expanded'}.png`,
        ),
        animations: 'disabled',
      });
      await navigation
        .getByRole('link', { name: 'All links', exact: true })
        .click();
      await page.getByRole('link', { name: 'portfolio', exact: true }).click();
      await expect(page.locator('.detail-meta')).toBeVisible();
      const meta = (await page.locator('.detail-meta').boundingBox())!;
      const danger = (await page.locator('.danger-zone').boundingBox())!;
      const editor = (await page.locator('.edit-form').boundingBox())!;
      expect(Math.abs(editor.width - meta.width)).toBeLessThan(1);
      expect(Math.abs(meta.height - danger.height)).toBeLessThan(1);
      expect(Math.abs(editor.y - meta.y)).toBeLessThan(3);
      expect(
        Math.abs(editor.y + editor.height - danger.y - danger.height),
      ).toBeLessThan(3);
      expect(Math.abs(meta.x - danger.x)).toBeLessThan(3);
      expect(danger.y - meta.y - meta.height).toBeGreaterThanOrEqual(20);
      expect(danger.y - meta.y - meta.height).toBeLessThanOrEqual(30);
      await page.screenshot({
        path: testInfo.outputPath(
          `details-${width}-${collapsed ? 'collapsed' : 'expanded'}.png`,
        ),
      });
      await page.getByRole('link', { name: 'View analytics' }).click();
      await expect(
        page.getByRole('heading', { name: 'Link analytics', exact: true }),
      ).toBeVisible();
      await expect(page.locator('.chart-panel')).toBeVisible();
      const analytics = (await content.boundingBox())!;
      expect(analytics.x + analytics.width).toBeCloseTo(width, 0);
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth > innerWidth,
        ),
      ).toBe(false);
      await page.screenshot({
        path: testInfo.outputPath(
          `analytics-${width}-${collapsed ? 'collapsed' : 'expanded'}.png`,
        ),
      });
      if (collapsed)
        await page.getByRole('button', { name: 'Expand sidebar' }).click();
    }
  }
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
  await page.getByRole('button', { name: 'Collapse sidebar' }).click();
  await page.setViewportSize({ width: 320, height: 844 });
  for (const name of ['All links', 'Overview', 'Create a link']) {
    const link = navigation.getByRole('link', { name, exact: true });
    await expect(link.locator('span')).toBeVisible();
    const bounds = (await link.boundingBox())!;
    expect(bounds.x).toBeGreaterThanOrEqual(0);
    expect(bounds.x + bounds.width).toBeLessThanOrEqual(320);
    expect(bounds.y).toBeGreaterThanOrEqual(0);
    expect(bounds.y + bounds.height).toBeLessThanOrEqual(844);
  }
  const signOut = page.getByRole('button', { name: 'Sign out', exact: true });
  await expect(signOut.locator('span')).toBeVisible();
  await expect(signOut).toBeInViewport({ ratio: 1 });
  await navigation
    .getByRole('link', { name: 'Create a link', exact: true })
    .click();
  await expect(page.getByLabel('Destination URL')).toBeVisible();
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

for (const width of [320, 390, 430]) {
  test(`phone shortener gives inputs and result actions room at ${width}px`, async ({
    page,
  }, testInfo) => {
    await page.setViewportSize({ width, height: 844 });
    await page.goto('/');
    const destination = page.getByLabel('Destination URL');
    const submit = page.getByRole('button', { name: 'Shorten URL' });
    await destination.waitFor();
    await page.evaluate(() => document.fonts.ready);
    const header = (await page.locator('.site-header').boundingBox())!;
    const input = (await destination.boundingBox())!;
    const button = (await submit.boundingBox())!;
    for (const control of [input, button]) {
      expect(control.x).toBeGreaterThanOrEqual(0);
      expect(control.x + control.width).toBeLessThanOrEqual(width);
      expect(control.y).toBeGreaterThanOrEqual(header.y + header.height);
      expect(control.y + control.height).toBeLessThanOrEqual(844);
    }
    expect(await page.evaluate(() => scrollY)).toBe(0);
    expect(input.width).toBeGreaterThanOrEqual(width - 80);
    const inputGap =
      Math.round((button.y - input.y - input.height) * 100) / 100;
    expect(inputGap).toBeGreaterThanOrEqual(12);
    await page.screenshot({ path: testInfo.outputPath('phone-form.png') });

    await destination.fill('https://example.com/a-long-story-to-share');
    await submit.click();
    const ticket = page.locator('.ticket-result');
    const result = page.getByLabel('Short URL', { exact: true });
    await expect(result).not.toHaveValue('');
    await ticket.evaluate(async (element) => {
      await Promise.all(
        element.getAnimations().map((animation) => animation.finished),
      );
    });
    expect(
      await result.evaluate((element) =>
        parseFloat(getComputedStyle(element).fontSize),
      ),
    ).toBeGreaterThanOrEqual(16);
    const content = await ticket.locator('.ticket-body').evaluate((element) => {
      const bounds = element.getBoundingClientRect();
      const style = getComputedStyle(element);
      const left = parseFloat(style.paddingLeft);
      const right = parseFloat(style.paddingRight);
      return { x: bounds.x + left, width: element.clientWidth - left - right };
    });
    for (const name of ['Copy link', 'View QR code']) {
      const action = ticket.getByRole('button', { name, exact: true });
      const bounds = (await action.boundingBox())!;
      expect(Math.abs(bounds.x - content.x)).toBeLessThan(1);
      expect(Math.abs(bounds.width - content.width)).toBeLessThan(1);
      expect(bounds.height).toBeGreaterThanOrEqual(48);
    }
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth > innerWidth,
      ),
    ).toBe(false);
    await page.screenshot({ path: testInfo.outputPath('phone-result.png') });
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
    if (width <= 560) {
      await expect(page.locator('.hero-link-illustration')).toBeHidden();
    } else {
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
    }
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
