import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';

export const FREEZE_UTC_MS = Date.UTC(2026, 10, 5, 2, 0, 0);

function parts(ms) {
  const total = Math.max(0, Math.floor(ms / 1000));
  return {
    d: Math.floor(total / 86400),
    h: Math.floor((total % 86400) / 3600),
    m: Math.floor((total % 3600) / 60),
    s: total % 60,
  };
}

function FreezeCountdown({ label, frozen }) {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);

  const left = FREEZE_UTC_MS - now;
  if (left <= 0) {
    return <div className="freeze is-frozen">{frozen}</div>;
  }
  const {
    d, h, m, s,
  } = parts(left);
  const urgent = left < 24 * 3600 * 1000;
  const pad = (n) => String(n).padStart(2, '0');
  return (
    <div className={urgent ? 'freeze is-urgent' : 'freeze'}>
      {`${label} ${d}d ${pad(h)}:${pad(m)}:${pad(s)}`}
    </div>
  );
}

FreezeCountdown.propTypes = {
  label: PropTypes.string.isRequired,
  frozen: PropTypes.string.isRequired,
};

export default FreezeCountdown;
