import PropTypes from 'prop-types';

function QueueWidget({ place, total, label }) {
  if (place == null) return null;
  const showBar = total != null && total > 0;
  const done = showBar ? Math.min(100, Math.max(0, ((total - place) / total) * 100)) : 0;
  return (
    <div className="queue">
      <div className="flap">
        <div className="half top" />
        <div className="half bottom" />
        <div key={place} className="fdigit tick">
          {place}
        </div>
        <div className="split" />
      </div>
      {showBar && (
        <div className="qbar" role="progressbar" aria-label={label} aria-valuenow={place} aria-valuemin={0} aria-valuemax={total}>
          <div className="qfill" style={{ width: `${done}%` }} />
        </div>
      )}
    </div>
  );
}

QueueWidget.propTypes = {
  place: PropTypes.number,
  total: PropTypes.number,
  label: PropTypes.string.isRequired,
};

QueueWidget.defaultProps = {
  place: null,
  total: null,
};

export default QueueWidget;
