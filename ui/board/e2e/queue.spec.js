import { test, expect } from '@playwright/test';
import fs from 'node:fs';

// The preview server serves dist/ statically; rewriting dist/board-state.json
// mid-test simulates the countdown the Python side writes during a demo.
const DIST = new URL('../dist/board-state.json', import.meta.url);
const SAMPLE = new URL('../public/board-state.sample.json', import.meta.url);

function seed(patch) {
  const board = JSON.parse(fs.readFileSync(SAMPLE, 'utf8'));
  const call = board.calls[board.calls.length - 1];
  if (patch) {
    call.position = 'queue';
    const turn = call.turns[call.turns.length - 1];
    turn.queue_place = patch.place;
    turn.queue_total = patch.total;
  }
  fs.writeFileSync(DIST, JSON.stringify(board));
}

test('queue ticket goes N/A -> 42 -> 0', async ({ page }) => {
  seed(null);
  await page.goto('/');
  const ticket = page.locator('.ovqueue .fdigit');
  await expect(ticket).toHaveText('N/A');
  await page.screenshot({ path: 'test-results/queue-na.png' });

  seed({ place: 42, total: 50 });
  await expect(ticket).toHaveText('42', { timeout: 15000 });
  await page.screenshot({ path: 'test-results/queue-42.png' });

  seed({ place: 0, total: 50 });
  await expect(ticket).toHaveText('0', { timeout: 15000 });
  await page.screenshot({ path: 'test-results/queue-0.png' });
});
