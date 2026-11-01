import { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import { setLevel } from '../audio';

const POLL_MS = 3000;
const MIN = 0.1;
const MAX = 4;
const STEP = 0.1;
const LOCAL_DEFAULT = 1.0;

async function getVolume() {
  const res = await fetch('/api/volume');
  if (!res.ok) {
    throw new Error(`volume fetch failed: ${res.status}`);
  }
  const data = await res.json();
  return Number(data.volume);
}

async function postVolume(value) {
  await fetch('/api/volume', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ volume: value.toFixed(1) }),
  });
}

function VolumeWidget({
  label, quieter, louder, browser,
}) {
  const [volume, setVolumeState] = useState(null);
  const [local, setLocal] = useState(false);
  const lastSet = useRef(0);
  const volumeRef = useRef(volume);
  volumeRef.current = volume;
  const localRef = useRef(local);
  localRef.current = local;

  useEffect(() => {
    let live = true;
    const load = async () => {
      if (localRef.current) {
        return;
      }
      try {
        const v = await getVolume();
        if (live && Date.now() - lastSet.current > POLL_MS) {
          setVolumeState(v);
          setLevel(v);
        }
      } catch {
        if (live && volumeRef.current == null) {
          setLocal(true);
          setVolumeState(LOCAL_DEFAULT);
          setLevel(LOCAL_DEFAULT);
        }
      }
    };
    load();
    const id = setInterval(load, POLL_MS);
    return () => {
      live = false;
      clearInterval(id);
    };
  }, []);

  useEffect(() => {
    const onKey = (event) => {
      if (event.metaKey || event.ctrlKey || event.altKey) {
        return;
      }
      const { target } = event;
      const isTextArea = target instanceof HTMLTextAreaElement;
      const isSelect = target instanceof HTMLSelectElement;
      if (isTextArea || isSelect) {
        return;
      }
      if (target instanceof HTMLInputElement && target.type !== 'range') {
        return;
      }
      const { current } = volumeRef;
      if (current == null) {
        return;
      }
      let delta = 0;
      if (event.key === '+' || event.key === '=' || event.key === 'Add') {
        delta = STEP;
      } else if (event.key === '-' || event.key === '_' || event.key === 'Subtract') {
        delta = -STEP;
      } else {
        return;
      }
      event.preventDefault();
      const v = Math.min(MAX, Math.max(MIN, Math.round((current + delta) * 10) / 10));
      lastSet.current = Date.now();
      setVolumeState(v);
      setLevel(v);
      if (!localRef.current) {
        postVolume(v);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => {
      window.removeEventListener('keydown', onKey);
    };
  }, []);

  if (volume == null) {
    return null;
  }

  const apply = (v) => {
    lastSet.current = Date.now();
    setVolumeState(v);
    setLevel(v);
    if (!local) {
      postVolume(v);
    }
  };

  const onChange = (event) => {
    apply(Number(event.target.value));
  };

  const nudge = (delta) => {
    const v = Math.min(MAX, Math.max(MIN, Math.round((volume + delta) * 10) / 10));
    apply(v);
  };

  return (
    <div className="vol">
      <span id="vol-text">{`${label} ${volume.toFixed(1)}`}</span>
      {local && <span className="voltag">{browser}</span>}
      <button type="button" className="volbtn" onClick={() => nudge(-STEP)} aria-label={quieter}>
        −
      </button>
      <input
        id="vol-slider"
        aria-labelledby="vol-text"
        type="range"
        min={MIN}
        max={MAX}
        step={STEP}
        value={volume}
        onChange={onChange}
      />
      <button type="button" className="volbtn" onClick={() => nudge(STEP)} aria-label={louder}>
        +
      </button>
    </div>
  );
}

VolumeWidget.propTypes = {
  label: PropTypes.string.isRequired,
  quieter: PropTypes.string.isRequired,
  louder: PropTypes.string.isRequired,
  browser: PropTypes.string.isRequired,
};

export default VolumeWidget;
