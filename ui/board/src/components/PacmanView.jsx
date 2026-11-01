import { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';

const COLS = 12;
const CELL = 56;
const PAD = 30;
const STEP_MS = 420;
const END_PAUSE = 4;

function cellPos(i) {
  const row = Math.floor(i / COLS);
  const col = row % 2 === 0 ? i % COLS : COLS - 1 - (i % COLS);
  return { x: PAD + col * CELL, y: PAD + row * CELL };
}

// Every tried word is a step; a miss steps back out before moving on,
// so blockages read as walls the walker bounces off.
function buildWalk(turns) {
  const walk = [];
  turns.forEach((turn, i) => {
    walk.push(i);
    if (!turn.ok && i > 0) {
      walk.push(i - 1);
    }
  });
  return walk;
}

function drawFrame(canvas, turns, walk, progress, now) {
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#0d1319';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const at = Math.min(progress, walk.length - 1);
  const head = Math.floor(at);
  const frac = at - head;
  const pos = (idx) => cellPos(walk[Math.max(0, Math.min(walk.length - 1, idx))]);

  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.strokeStyle = '#134e4a';
  ctx.lineWidth = 12;
  ctx.beginPath();
  walk.slice(0, head + 1).forEach((cell, i) => {
    const p = cellPos(cell);
    if (i === 0) {
      ctx.moveTo(p.x, p.y);
    } else {
      ctx.lineTo(p.x, p.y);
    }
  });
  ctx.stroke();

  turns.forEach((turn, i) => {
    const p = cellPos(i);
    const visited = walk.slice(0, head + 1).includes(i);
    if (!turn.ok && visited) {
      ctx.fillStyle = '#7f1d1d';
      ctx.fillRect(p.x - 13, p.y - 13, 26, 26);
      ctx.fillStyle = '#f87171';
      ctx.font = '13px ui-monospace, monospace';
      ctx.textAlign = 'center';
      ctx.fillText('×', p.x, p.y + 5);
    }
    if (turn.ok && !visited) {
      ctx.fillStyle = '#2dd4bf';
      ctx.beginPath();
      ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.fillStyle = visited ? '#c8cfd8' : '#5b6570';
    ctx.font = '9px ui-monospace, monospace';
    ctx.textAlign = 'center';
    const word = turn.word.length > 12 ? `${turn.word.slice(0, 11)}…` : turn.word;
    ctx.fillText(word, p.x, p.y + 26);
  });

  const a = pos(head);
  const b = pos(head + 1);
  const px = a.x + (b.x - a.x) * frac;
  const py = a.y + (b.y - a.y) * frac;
  const mouth = (now / 160) % 2 < 1 ? 0.35 : 0.02;
  const angle = Math.atan2(b.y - a.y, b.x - a.x);
  ctx.fillStyle = '#eab308';
  ctx.beginPath();
  ctx.moveTo(px, py);
  ctx.arc(px, py, 11, angle + mouth, angle + Math.PI * 2 - mouth);
  ctx.closePath();
  ctx.fill();
}

function PacmanView({ calls, t }) {
  const ref = useRef(null);
  const turns = [];
  calls.forEach((call) => {
    (call.turns ?? []).forEach((turn) => {
      turns.push({ word: turn.caller ?? '', ok: turn.matched === true });
    });
  });

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas || turns.length === 0) {
      return undefined;
    }
    const walk = buildWalk(turns);
    const rows = Math.max(1, Math.ceil(turns.length / COLS));
    canvas.width = COLS * CELL + PAD * 2;
    canvas.height = rows * CELL + PAD * 2;
    const reduced = typeof window !== 'undefined'
      && typeof window.matchMedia === 'function'
      && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced || walk.length < 2) {
      drawFrame(canvas, turns, walk, walk.length - 1, 0);
      return undefined;
    }
    let raf = 0;
    const start = performance.now();
    const tick = (now) => {
      const cycle = walk.length - 1 + END_PAUSE;
      const progress = ((now - start) / STEP_MS) % cycle;
      drawFrame(canvas, turns, walk, progress, now);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf);
    };
  }, [calls]);

  if (turns.length === 0) {
    return <p className="sub">{t.noLessons}</p>;
  }
  return (
    <div className="maze">
      <canvas ref={ref} className="mazecv" aria-label={t.maze} />
      <p className="mazelegend">
        <span className="sw path" aria-hidden="true" />
        {t.explored}
        {' · '}
        <span className="sw pellet" aria-hidden="true" />
        {t.transfers}
        {' · '}
        <span className="sw wall" aria-hidden="true" />
        {t.missed}
      </p>
      <p className="sub">{t.hintCoverage}</p>
    </div>
  );
}

PacmanView.propTypes = {
  calls: PropTypes.arrayOf(PropTypes.shape({
    turns: PropTypes.arrayOf(PropTypes.shape({
      caller: PropTypes.string,
      matched: PropTypes.bool,
    })),
  })).isRequired,
  t: PropTypes.shape({
    maze: PropTypes.string.isRequired,
    explored: PropTypes.string.isRequired,
    transfers: PropTypes.string.isRequired,
    missed: PropTypes.string.isRequired,
    hintCoverage: PropTypes.string.isRequired,
    noLessons: PropTypes.string.isRequired,
  }).isRequired,
};

export default PacmanView;
