// README screenshots for the Holdmate board.
//
// Reuses the pattern from ui/board/e2e/queue.spec.js: seed
// ui/board/dist/board-state.json from ui/board/public/board-state.sample.json
// and serve dist/ via `vite preview` on an odd port.
//
// Usage (from repo root):
//   PLAYWRIGHT_BROWSERS_PATH=/tmp/pw-browsers node docs/capture-screens.mjs
//
// Writes only: docs/images/board-{overview,queue,lessons,pacman}.png
// Restores dist/board-state.json to its prior content on exit.

import { spawn } from 'node:child_process';
import fs from 'node:fs';
import { createRequire } from 'node:module';

const boardRequire = createRequire(new URL('../ui/board/package.json', import.meta.url));
const { chromium } = boardRequire('@playwright/test');

const ROOT = new URL('../', import.meta.url);
const BOARD_DIR = new URL('../ui/board/', import.meta.url);
const DIST = new URL('../ui/board/dist/board-state.json', import.meta.url);
const SAMPLE = new URL('../ui/board/public/board-state.sample.json', import.meta.url);
const IMAGES = new URL('./images/', import.meta.url);

const PORT = 5197; // odd, and clear of the 5199 in playwright.config.js
const BASE = `http://localhost:${PORT}/`;
const VIEWPORT = { width: 1280, height: 800 };

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

function startServer() {
  const child = spawn('npm', ['run', 'preview', '--', '--port', String(PORT), '--strictPort'], {
    cwd: BOARD_DIR,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  return child;
}

async function waitForServer(timeoutMs = 60000) {
  const start = Date.now();
  for (;;) {
    try {
      const res = await fetch(BASE);
      if (res.ok) return;
    } catch {
      // not up yet
    }
    if (Date.now() - start > timeoutMs) {
      throw new Error(`preview server did not come up on ${BASE}`);
    }
    await new Promise((r) => { setTimeout(r, 500); });
  }
}

async function main() {
  fs.mkdirSync(IMAGES, { recursive: true });
  const backup = fs.existsSync(DIST) ? fs.readFileSync(DIST) : null;

  seed(null);
  const server = startServer();
  const browser = await chromium.launch();
  try {
    await waitForServer();
    const page = await browser.newPage({ viewport: VIEWPORT });
    await page.goto(BASE, { waitUntil: 'networkidle' });

    const ticket = page.locator('.ovqueue .fdigit');
    await page.waitForFunction(
      (sel) => document.querySelector(sel)?.textContent?.trim() === 'N/A',
      '.ovqueue .fdigit',
      { timeout: 15000 },
    );
    await page.screenshot({ path: new URL('board-overview.png', IMAGES).pathname });
    console.log('wrote board-overview.png (overview tab, queue N/A)');

    seed({ place: 42, total: 50 });
    await page.waitForFunction(
      (sel) => document.querySelector(sel)?.textContent?.trim() === '42',
      '.ovqueue .fdigit',
      { timeout: 15000 },
    );
    await ticket.scrollIntoViewIfNeeded();
    await page.screenshot({ path: new URL('board-queue.png', IMAGES).pathname });
    console.log('wrote board-queue.png (overview tab, queue place 42)');

    const lessonsTab = page.getByRole('button', { name: 'Lessons' });
    if (await lessonsTab.count() > 0) {
      await lessonsTab.click();
      await page.waitForTimeout(800);
      await page.screenshot({ path: new URL('board-lessons.png', IMAGES).pathname });
      console.log('wrote board-lessons.png (lessons tab)');
    } else {
      console.log('SKIPPED board-lessons.png: no Lessons tab found');
    }

    const mazeTab = page.getByRole('button', { name: 'Maze' });
    if (await mazeTab.count() > 0) {
      await mazeTab.click();
      await page.locator('canvas.mazecv').waitFor({ timeout: 15000 }).catch(() => {});
      await page.waitForTimeout(1500); // let the walker animate a few steps
      await page.screenshot({ path: new URL('board-pacman.png', IMAGES).pathname });
      console.log('wrote board-pacman.png (maze/pacman tab)');
    } else {
      console.log('SKIPPED board-pacman.png: no Maze tab found');
    }
  } finally {
    await browser.close().catch(() => {});
    server.kill('SIGKILL');
    if (backup === null) {
      if (fs.existsSync(DIST)) fs.rmSync(DIST);
    } else {
      fs.writeFileSync(DIST, backup);
    }
    console.log(`restored dist/board-state.json (repo root: ${ROOT.pathname})`);
  }
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
