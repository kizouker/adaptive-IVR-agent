import PropTypes from 'prop-types';
import Typewriter from './Typewriter';

function Subtitle({ text, who }) {
  if (!text) return null;
  return (
    <div className="subs" aria-live="polite">
      <div className="subline">
        <div className="subwho">{who}</div>
        <div className="subtext"><Typewriter text={text} /></div>
      </div>
    </div>
  );
}

Subtitle.propTypes = {
  text: PropTypes.string,
  who: PropTypes.string.isRequired,
};

Subtitle.defaultProps = {
  text: null,
};

export default Subtitle;
