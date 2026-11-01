import PropTypes from 'prop-types';

const stringsShape = PropTypes.shape({
  errand: PropTypes.string.isRequired,
  caller: PropTypes.string.isRequired,
  robot: PropTypes.string.isRequired,
  state: PropTypes.string.isRequired,
  routed: PropTypes.string.isRequired,
  missed: PropTypes.string.isRequired,
});

function CallThread({ call, lang, t }) {
  return (
    <div className="card">
      <h3>{call.label}</h3>
      <div className="errand">{`${t.errand}: ${call.errand}`}</div>
      {call.turns.map((turn) => (
        <div key={turn.caller}>
          <div className="turn caller">
            <div className="who">{t.caller}</div>
            <div className="bubble">{turn.caller}</div>
          </div>
          <div className="turn robot">
            <div className="who">{t.robot}</div>
            <div className="bubble">{turn.robot}</div>
            <div className="meta">
              <span className="badge">{`${t.state}: ${turn.state_name[lang]}`}</span>
              {turn.matched
                ? <span className="kw-ok">{`${turn.caller} → ${t.routed}`}</span>
                : <span className="kw-miss">{t.missed}</span>}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

CallThread.propTypes = {
  call: PropTypes.shape({
    label: PropTypes.string.isRequired,
    errand: PropTypes.string.isRequired,
    turns: PropTypes.arrayOf(PropTypes.shape({
      caller: PropTypes.string.isRequired,
      robot: PropTypes.string.isRequired,
      matched: PropTypes.bool.isRequired,
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
