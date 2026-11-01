import { useState } from 'react';
import PropTypes from 'prop-types';
import Typewriter from './Typewriter';

const stringsShape = PropTypes.shape({
  errand: PropTypes.string.isRequired,
  caller: PropTypes.string.isRequired,
  robot: PropTypes.string.isRequired,
  state: PropTypes.string.isRequired,
  routed: PropTypes.string.isRequired,
  missed: PropTypes.string.isRequired,
  captions: PropTypes.string.isRequired,
  queuePlace: PropTypes.string.isRequired,
  history: PropTypes.string.isRequired,
  showLess: PropTypes.string.isRequired,
});

function CallThread({ call, lang, t }) {
  const [expanded, setExpanded] = useState(false);
  const ordered = [...call.turns].reverse();
  return (
    <div className="card">
      <h3>{call.label}</h3>
      <div className="errand">{`${t.errand}: ${call.errand}`}</div>
      {expanded && ordered.map((turn) => (
        <div key={turn.caller_audio || `${turn.caller}|${turn.robot}`}>
          {turn.caller !== '' && (
            <div className="turn caller">
              <div className="who">{call.caller_name || t.caller}</div>
              <div className="bubble"><Typewriter text={turn.caller} /></div>
              {turn.caller_audio && (
                <audio controls src={turn.caller_audio} aria-label={call.caller_name || t.caller}>
                  <track kind="captions" src={turn.caller_captions} srcLang={lang} label={t.captions} />
                </audio>
              )}
            </div>
          )}
          <div className="turn robot">
            <div className="who">{call.robot_name || t.robot}</div>
            <div className="bubble"><Typewriter text={turn.robot} /></div>
            {turn.robot_audio && (
              <audio controls src={turn.robot_audio} aria-label={call.robot_name || t.robot}>
                <track kind="captions" src={turn.robot_captions} srcLang={lang} label={t.captions} />
              </audio>
            )}
            <div className="meta">
              <span className="badge">{`${t.state}: ${turn.state_name[lang]}`}</span>
              {turn.queue_place != null && (
                <span className="badge">{`${t.queuePlace} ${turn.queue_place}`}</span>
              )}
              {turn.caller !== '' && (turn.matched
                ? <span className="kw-ok">{`${turn.caller} → ${t.routed}`}</span>
                : <span className="kw-miss">{t.missed}</span>)}
            </div>
          </div>
        </div>
      ))}
      {call.turns.length > 0 && (
        <button type="button" className="linklike" onClick={() => setExpanded(!expanded)}>
          {expanded ? t.showLess : `${t.history} (${call.turns.length})`}
        </button>
      )}
    </div>
  );
}

CallThread.propTypes = {
  call: PropTypes.shape({
    label: PropTypes.string.isRequired,
    errand: PropTypes.string.isRequired,
    caller_name: PropTypes.string,
    robot_name: PropTypes.string,
    turns: PropTypes.arrayOf(PropTypes.shape({
      caller: PropTypes.string.isRequired,
      robot: PropTypes.string.isRequired,
      matched: PropTypes.bool.isRequired,
      caller_audio: PropTypes.string,
      robot_audio: PropTypes.string,
      caller_captions: PropTypes.string,
      robot_captions: PropTypes.string,
      queue_place: PropTypes.number,
      state_name: PropTypes.shape({
        sv: PropTypes.string.isRequired,
        en: PropTypes.string.isRequired,
      }).isRequired,
    })).isRequired,
  }).isRequired,
  lang: PropTypes.oneOf(['sv', 'en']).isRequired,
  t: stringsShape.isRequired,
};

export default CallThread;
