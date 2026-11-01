// Shared browser playback level (0.1-4.0, 1 = normal). The volume widget
// writes it; keypad beeps and the fake CLI read it. Always local to the
// page: on the live board it mirrors the talk volume, on Pages it is the
// only volume there is.
let level = 1.0;
const listeners = new Set();

export function getLevel() {
  return level;
}

export function setLevel(value) {
  level = value;
  listeners.forEach((fn) => fn(value));
}

export function onLevel(fn) {
  listeners.add(fn);
  return () => {
    listeners.delete(fn);
  };
}

// speechSynthesis volume is 0-1; talk scale 1.0 already means full here.
export function speechVolume() {
  return Math.min(1, Math.max(0, level));
}

// Keypad beep base 0.25 at level 1, boosted up to x2.
export function beepGain() {
  return 0.25 * Math.min(2, Math.max(0.1, level));
}

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

export function dtmf(key) {
  const pair = FREQS[key];
  if (!pair || typeof window === 'undefined') return;
  try {
    ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === 'suspended') ctx.resume();
    const t0 = ctx.currentTime;
    const gainLevel = beepGain();
    pair.forEach((freq) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(gainLevel, t0);
      gain.gain.setValueAtTime(gainLevel, t0 + 0.22);
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
