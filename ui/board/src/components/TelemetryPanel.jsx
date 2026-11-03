import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';

const POLL_MS = 5000;
const MAX_ROWS = 8;

function shortModel(model) {
  return String(model || '').replace('meta-models/', '');
}

function TelemetryPanel({ t }) {
  const [rows, setRows] = useState(null);

  useEffect(() => {
    let live = true;
    const load = async () => {
      try {
        const res = await fetch('telemetry.json');
        if (!res.ok) {
          throw new Error(`telemetry fetch failed: ${res.status}`);
        }
        if (live) {
          setRows(await res.json());
        }
      } catch {
        if (live) {
          setRows([]);
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

  if (rows === null) {
    return null;
  }
  if (rows.length === 0) {
    return <div className="telemetry">{t.noCalls}</div>;
  }
  return (
    <table className="telemetry">
      <thead>
        <tr>
          <th>{t.model}</th>
          <th>{t.runtime}</th>
          <th>{t.latency}</th>
          <th>{t.keyword}</th>
        </tr>
      </thead>
      <tbody>
        {rows.slice(-MAX_ROWS).reverse().map((row, i) => (
          <tr key={`${row.heard_sha256 || 'na'}-${i}`}>
            <td>{shortModel(row.model)}</td>
            <td>{row.runtime}</td>
            <td>{`${row.latency_ms} ms`}</td>
            <td>{row.keyword || '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

TelemetryPanel.propTypes = {
  t: PropTypes.objectOf(PropTypes.string).isRequired,
};

export default TelemetryPanel;
