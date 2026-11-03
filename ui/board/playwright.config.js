import { defineConfig } from '@playwright/test';

// BOARD_URL targets an external board (Docker container, Azure): no local
// webServer is started. Without it, e2e spins the local preview server.
// Example: BOARD_URL=http://localhost:8080 npx playwright test
const externalUrl = process.env.BOARD_URL || '';

export default defineConfig({
  testDir: './e2e',
  timeout: 60000,
  use: { baseURL: externalUrl || 'http://localhost:5199' },
  ...(externalUrl ? {} : {
    webServer: {
      command: 'npm run preview -- --port 5199 --strictPort',
      url: 'http://localhost:5199',
      reuseExistingServer: !process.env.CI,
      timeout: 60000,
    },
  }),
});
