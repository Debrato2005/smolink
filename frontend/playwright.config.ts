import { defineConfig, devices } from '@playwright/test';
const production = process.env.SMOLINK_E2E_TARGET === 'production';
// Optional host-provided Chromium when the pinned runtime cannot be downloaded.
// A substitute binary is an environment note, not a pinned-engine pass.
const chromiumPath = process.env.SMOLINK_CHROMIUM_PATH;
const baseURL = production ? 'http://127.0.0.1:4173' : 'http://127.0.0.1:3100';
export default defineConfig({
  testDir: './tests/e2e',
  outputDir: production ? 'test-results/production' : 'test-results/fixture',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  testMatch: production
    ? '**/production.spec.ts'
    : '**/{smoke,product}.spec.ts',
  workers: 3,
  retries: process.env.CI ? 1 : 0,
  reporter: 'list',
  use: { baseURL, trace: 'retain-on-failure' },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        ...(chromiumPath
          ? { launchOptions: { executablePath: chromiumPath } }
          : {}),
      },
    },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  webServer: {
    command: production ? 'npm run preview' : 'npm run dev -- --port 3100',
    url: baseURL,
    reuseExistingServer: process.env.SMOLINK_E2E_REUSE === '1',
  },
});
