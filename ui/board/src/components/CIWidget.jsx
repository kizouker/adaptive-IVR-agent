import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';

const API = 'https://api.github.com/repos/kizouker/adaptive-IVR-agent/actions/runs?per_page=5';
const ACTIONS_URL = 'https://github.com/kizouker/adaptive-IVR-agent/actions';
const POLL_MS = 5 * 60 * 1000;

function mark(run) {
  if (run.status !== 'completed') {
    return ['●', 'run'];
  }
  return run.conclusion === 'success' ? ['✔', 'ok'] : ['✘', 'bad'];
}

function CIWidget({ label, all }) {
  const [runs, setRuns] = useState(null);

  useEffect(() => {
    let live = true;
    const load = async () => {
      try {
        const res = await fetch(API);
        if (!res.ok) {
          throw new Error(`ci fetch failed: ${res.status}`);
        }
        const data = await res.json();
        if (live) {
          setRuns(data.workflow_runs || []);
        }
      } catch {
        if (live) {
          setRuns([]);
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

  if (runs === null) {
    return null;
  }
  return (
    <div className="ci">
      <span>{label}</span>
      {runs.map((run) => {
        const [glyph, cls] = mark(run);
        const when = `${run.created_at.slice(0, 10)} ${run.created_at.slice(11, 16)} UTC`;
        return (
          <a
            key={run.id}
            className={cls}
            href={run.html_url}
            target="_blank"
            rel="noreferrer"
            title={`${run.name} ${when}`}
          >
            {`${glyph} ${run.name} ${run.head_sha.slice(0, 7)}`}
          </a>
        );
      })}
      <a href={ACTIONS_URL} target="_blank" rel="noreferrer">{all}</a>
    </div>
  );
}

CIWidget.propTypes = {
  label: PropTypes.string.isRequired,
  all: PropTypes.string.isRequired,
};

export default CIWidget;
