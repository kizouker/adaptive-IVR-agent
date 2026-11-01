import { useState } from 'react';
import PropTypes from 'prop-types';

const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#'];

// DTMF pairs, mirrored from tones.py so the browser beep matches the Mac one.
const FREQS = {
  1: [697, 1209],
  2: [697, 1336],
  3: [697, 1477],
  4: [770, 1209],
  5: [770, 1336],
  6: [770, 1477],
  7: [852, 1209],
  8: [852, 1336],
  9: [852, 1477],
  '*': [941, 1209],
  0: [941, 1336],
  '#': [941, 1477],
};

let ctx = null;

function beep(key) {
  const pair = FREQS[key];
  if (!pair || typeof window === 'undefined') return;
  try {
    ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === 'suspended') ctx.resume();
    const t0 = ctx.currentTime;
    pair.forEach((freq) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.25, t0);
      gain.gain.setValueAtTime(0.25, t0 + 0.22);
      gain.gain.exponentialRampToValueAtTime(0.001, t0 + 0.25);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(t0);
      osc.stop(t0 + 0.26);
    });
  } catch {
    // Silent keypad is still a working keypad.
  }
}

async function sendDigit(key) {
  try {
    await fetch('/api/dtmf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ digit: key }),
    });
  } catch {
    // Static site (Pages): local beep only, nothing listens.
  }
}

function KeypadWidget({ label }) {
  const [last, setLast] = useState(null);
  const press = (key) => {
    beep(key);
    setLast(key);
    sendDigit(key);
  };
  return (
    <div className="keypad" role="group" aria-label={label}>
      {KEYS.map((key) => (
        <button
          key={key}
          type="button"
          className={key === last ? 'kkey hit' : 'kkey'}
          onClick={() => press(key)}
          aria-label={key}
        >
          {key}
        </button>
      ))}
    </div>
  );
}

KeypadWidget.propTypes = {
  label: PropTypes.string.isRequired,
};

export default KeypadWidget;
