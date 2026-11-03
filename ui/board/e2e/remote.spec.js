import { test, expect } from '@playwright/test';

// Remote board smoke: read-only, works against Docker and Azure (#169).
// The queue countdown spec needs local dist/ writes, so it stays local-only.
test('remote board serves front page, state and version', async ({ page, request }) => {
  await page.goto('/');
  await expect(page.locator('body')).toContainText('Holdmate');

  const state = await request.get('board-state.json');
  expect(state.ok()).toBe(true);
  const board = await state.json();
  expect(board.calls.length).toBeGreaterThan(0);

  const version = await request.get('version.json');
  expect(version.ok()).toBe(true);
  expect((await version.json()).version).toBeTruthy();
});
