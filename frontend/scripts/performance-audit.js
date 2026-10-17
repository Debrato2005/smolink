import { chromium } from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';
const stage = process.argv[2] ?? 'before';
const base = process.env.AUDIT_URL ?? 'http://127.0.0.1:4173';
const out = path.resolve('.local/performance', stage);
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch();
const samples = [];
try {
  if (!process.env.SKIP_METRICS)
    for (const mobile of [false, true])
      for (let run = 0; run < Number(process.env.SAMPLE_RUNS ?? 3); run++) {
        const context = await browser.newContext({
          viewport: mobile
            ? { width: 390, height: 844 }
            : { width: 1440, height: 900 },
          deviceScaleFactor: mobile ? 2 : 1,
          isMobile: mobile,
          hasTouch: mobile,
        });
        const page = await context.newPage();
        // Keep the external badge deterministic. Its production latency is separate.
        await page.route('https://img.shields.io/**', (route) =>
          route.fulfill({
            contentType: 'image/svg+xml',
            body: '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="24"><text x="4" y="18">0</text></svg>',
          }),
        );
        const cdp = await context.newCDPSession(page);
        await cdp.send('Network.enable');
        await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
        await cdp.send('Performance.enable');
        if (mobile) {
          await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
          await cdp.send('Network.emulateNetworkConditions', {
            offline: false,
            latency: 150,
            downloadThroughput: 1600000 / 8,
            uploadThroughput: 750000 / 8,
          });
        }
        await page.addInitScript(() => {
          window.audit = { lcp: 0, cls: 0, longTasks: [], events: [] };
          new PerformanceObserver((list) => {
            for (const e of list.getEntries()) window.audit.lcp = e.startTime;
          }).observe({ type: 'largest-contentful-paint', buffered: true });
          new PerformanceObserver((list) => {
            for (const e of list.getEntries())
              if (!e.hadRecentInput) window.audit.cls += e.value;
          }).observe({ type: 'layout-shift', buffered: true });
          new PerformanceObserver((list) => {
            for (const e of list.getEntries())
              window.audit.longTasks.push(e.duration);
          }).observe({ type: 'longtask', buffered: true });
          new PerformanceObserver((list) => {
            for (const e of list.getEntries())
              window.audit.events.push({
                name: e.name,
                duration: e.duration,
                interactionId: e.interactionId,
              });
          }).observe({ type: 'event', buffered: true, durationThreshold: 16 });
        });
        const errors = [];
        page.on('pageerror', (e) => errors.push(e.message));
        page.on('console', (m) => {
          if (m.type() === 'error') errors.push(m.text());
        });
        if (run === 0)
          await cdp.send('Tracing.start', {
            categories: 'devtools.timeline,v8,blink.user_timing',
            transferMode: 'ReturnAsStream',
          });
        await page.goto(base, { waitUntil: 'networkidle' });
        await page.getByLabel('Destination URL').waitFor();
        await page.evaluate(() => document.fonts.ready);
        await page.evaluate(() =>
          Promise.all(
            Array.from(document.images, (image) =>
              image.decode().catch(() => {}),
            ),
          ),
        );
        await page.waitForTimeout(700);
        const initial = await page.evaluate(() => ({
          ...window.audit,
          fcp:
            performance.getEntriesByName('first-contentful-paint')[0]
              ?.startTime ?? null,
          ttfb: performance.getEntriesByType('navigation')[0].responseStart,
          resources: performance.getEntriesByType('resource').map((e) => ({
            name: new URL(e.name).pathname,
            bytes: e.encodedBodySize,
            transfer: e.transferSize,
            duration: e.duration,
          })),
          navigation: performance.getEntriesByType('navigation')[0].toJSON(),
        }));
        await page
          .getByLabel('Destination URL')
          .pressSequentially('https://example.com/performance', { delay: 30 });
        await page.getByLabel('Set an expiry').check();
        await page.getByLabel('Expiry date and time').click();
        await page.getByLabel('Date', { exact: true }).waitFor();
        await page.waitForTimeout(500);
        const events = await page.evaluate(() => window.audit.events);
        const metrics = await cdp.send('Performance.getMetrics');
        samples.push({
          mobile,
          run,
          initial,
          events,
          metrics: Object.fromEntries(
            metrics.metrics.map((m) => [m.name, m.value]),
          ),
          errors,
        });
        if (run === 0) {
          const done = new Promise((resolve) =>
            cdp.once('Tracing.tracingComplete', resolve),
          );
          await cdp.send('Tracing.end');
          const { stream } = await done;
          let trace = '';
          for (;;) {
            const chunk = await cdp.send('IO.read', { handle: stream });
            trace += chunk.data;
            if (chunk.eof) break;
          }
          await cdp.send('IO.close', { handle: stream });
          await fs.writeFile(
            path.join(out, `${mobile ? 'mobile' : 'desktop'}-trace.json`),
            trace,
          );
        }
        await context.close();
      }
  if (!process.env.SKIP_METRICS)
    await fs.writeFile(
      path.join(out, 'metrics.json'),
      JSON.stringify(samples, null, 2),
    );
  if (!process.env.SKIP_SHOTS)
    for (const width of [390, 768, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 900 } });
      await page.route('https://img.shields.io/**', (route) =>
        route.fulfill({
          contentType: 'image/svg+xml',
          body: '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="24"><text x="4" y="18">0</text></svg>',
        }),
      );
      await page.route('**/api/v1/urls', (route) =>
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 123,
            short_code: 'perf',
            short_url: 'https://short.example/perf',
            destination: 'https://example.com/',
            created_at: '2026-10-06T09:00:00Z',
            expires_at: null,
          }),
        }),
      );
      const capture = async (name) => {
        await page.evaluate(() => {
          window.scrollTo({ top: 0, behavior: 'instant' });
          return document.fonts.ready;
        });
        await page.evaluate(() =>
          Promise.all(
            Array.from(document.images, (image) =>
              image.decode().catch(() => {}),
            ),
          ),
        );
        await page.mouse.move(0, 0);
        await page.waitForTimeout(700);
        await page.screenshot({
          path: path.join(out, `${width}-${name}.png`),
          fullPage: true,
        });
      };
      await page.goto(base);
      await page.getByLabel('Destination URL').waitFor();
      await capture('home');
      await page.getByLabel('Destination URL').focus();
      await capture('focus');
      await page.getByRole('button', { name: 'Shorten URL' }).click();
      await capture('validation');
      await page.getByLabel('Destination URL').fill('https://example.com');
      await page.getByRole('button', { name: 'Shorten URL' }).click();
      await page.getByLabel('Short URL', { exact: true }).waitFor();
      await capture('success');
      await page
        .getByRole('button', { name: 'Contact me', exact: true })
        .first()
        .click();
      await page.getByRole('dialog').waitFor();
      await capture('contact');
      await page.getByRole('button', { name: 'Close dialog' }).click();
      if (width < 1261) {
        await page.getByRole('button', { name: 'Open navigation' }).click();
        await capture('menu');
      }
      for (const route of [
        '/login',
        '/register',
        '/verify-email',
        '/forgot-password',
        '/reset-password',
        '/resend-verification',
        '/dashboard',
        '/dashboard/urls/1/analytics',
        '/missing',
      ]) {
        await page.goto(base + route);
        await page.locator('main h1').waitFor();
        await capture(route.slice(1).replaceAll('/', '-'));
      }
      await page.goto(base);
      await page.getByLabel('Destination URL').waitFor();
      await page.route('**/api/v1/urls', (route) =>
        route.fulfill({
          status: 503,
          contentType: 'application/json',
          body: '{}',
        }),
      );
      await page.getByLabel('Destination URL').fill('https://example.com');
      await page.getByRole('button', { name: 'Shorten URL' }).click();
      await page.getByRole('alert').waitFor();
      await capture('error');
      await page.close();
    }
  console.log(
    JSON.stringify(
      samples.map((s) => ({
        mobile: s.mobile,
        run: s.run,
        lcp: s.initial.lcp,
        fcp: s.initial.fcp,
        cls: s.initial.cls,
        tbt: s.initial.longTasks.reduce((n, d) => n + Math.max(0, d - 50), 0),
        js: s.initial.resources
          .filter((r) => r.name.endsWith('.js'))
          .reduce((n, r) => n + r.bytes, 0),
        requests: s.initial.resources.length,
        errors: s.errors,
      })),
    ),
  );
} finally {
  await browser.close();
}
