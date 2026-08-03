// @ts-check
const { defineConfig, devices } = require('@playwright/test');
const path = require('path');

module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  workers: 1,
  timeout: 90000,
  expect: {
    timeout: 15000
  },
  reporter: [
    ['list'],
    ['html', { outputFolder: 'reports/html-report', open: 'never' }],
    ['json', { outputFile: 'reports/execution-results.json' }],
    ['junit', { outputFile: 'reports/junit-results.xml' }]
  ],
  use: {
    testIdAttribute: 'data-test',
    channel: 'chrome',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 20000,
    navigationTimeout: 45000,
    launchOptions: {
      args: ['--disable-blink-features=AutomationControlled']
    }
  },
  projects: [
    {
      name: 'ui-chromium',
      testDir: './tests/ui',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
        baseURL: 'https://practicesoftwaretesting.com',
        userAgent:
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale: 'en-US',
        extraHTTPHeaders: {
          'Accept-Language': 'en-US,en;q=0.9'
        }
      }
    },
    {
      name: 'api',
      testDir: './tests/api',
      use: {
        baseURL: 'https://api.practicesoftwaretesting.com'
      }
    }
  ],
  outputDir: path.join(__dirname, 'reports/test-results')
});
