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

function VolumeWidget({ label }) {
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

  const onChange = (event) => {
    const v = Number(event.target.value);
    lastSet.current = Date.now();
    setVolumeState(v);
    postVolume(v);
  };

  return (
    <label className="vol" htmlFor="vol-slider">
      {`${label} ${volume.toFixed(1)}`}
      <input
        id="vol-slider"
        type="range"
        min={MIN}
        max={MAX}
        step={STEP}
        value={volume}
        onChange={onChange}
      />
    </label>
  );
}

VolumeWidget.propTypes = {
  label: PropTypes.string.isRequired,
};

export default VolumeWidget;
