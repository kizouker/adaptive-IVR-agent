import PropTypes from 'prop-types';

const nodeClass = (index, position) => {
  if (index < position) return 'node done';
  if (index === position) return 'node current';
  return 'node';
};

function ProcessHeader({
  states, positionId, lang, levelWord,
}) {
  const position = states.findIndex((state) => state.id === positionId);
  return (
    <div className="pipe">
      {states.map((state, index) => (
        <div key={state.id} className={nodeClass(index, position)}>
          <span className="n">{`${levelWord} ${index + 1}`}</span>
          {state[lang]}
        </div>
      ))}
    </div>
  );
}

ProcessHeader.propTypes = {
  states: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
    sv: PropTypes.string.isRequired,
    en: PropTypes.string.isRequired,
  })).isRequired,
  positionId: PropTypes.string.isRequired,
  lang: PropTypes.oneOf(['sv', 'en']).isRequired,
  levelWord: PropTypes.string.isRequired,
};

export default ProcessHeader;
