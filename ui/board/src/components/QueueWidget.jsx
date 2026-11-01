import PropTypes from 'prop-types';

function QueueWidget({ place }) {
  const empty = place == null;
  return (
    <div className="queue">
      <div className={empty ? 'flap dim' : 'flap'}>
        <div className="half top" />
        <div className="half bottom" />
        <div key={empty ? 'none' : place} className="fdigit tick">
          {empty ? '–' : place}
        </div>
        <div className="split" />
      </div>
    </div>
  );
}

QueueWidget.propTypes = {
  place: PropTypes.number,
};

QueueWidget.defaultProps = {
  place: null,
};

export default QueueWidget;
