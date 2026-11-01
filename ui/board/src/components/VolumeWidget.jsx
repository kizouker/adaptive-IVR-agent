import { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';

const POLL_MS = 3000;
const MIN = 0.1;
const MAX = 4;
const STEP = 0.1;

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

function VolumeWidget({ label, quieter, louder }) {
  const [volume, setVolumeState] = useState(null);
  const lastSet = useRef(0);

  useEffect(() => {
    let live = true;
    const load = async () => {
      try {
        const v = await getVolume();
        if (live && Date.now() - lastSet.current > POLL_MS) {
          setVolumeState(v);
        }
      } catch {
        if (live) {
          setVolumeState(null);
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

  if (volume == null) {
    return null;
  }

  const apply = (v) => {
    lastSet.current = Date.now();
    setVolumeState(v);
    postVolume(v);
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
};

export default VolumeWidget;
