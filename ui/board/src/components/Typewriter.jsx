import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';

const CHAR_MS = 7;

function prefersReducedMotion() {
  return typeof window !== 'undefined'
    && typeof window.matchMedia === 'function'
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function Typewriter({ text }) {
  const [shown, setShown] = useState('');
  useEffect(() => {
    if (prefersReducedMotion()) {
      setShown(text);
      return undefined;
    }
    const id = setInterval(() => {
      setShown((prev) => {
        if (prev.length >= text.length) {
          clearInterval(id);
          return prev;
        }
        return text.slice(0, prev.length + 1);
      });
    }, CHAR_MS);
    return () => clearInterval(id);
  }, [text]);
  return (
    <span>
      {shown}
      {shown.length < text.length && <span className="caret" aria-hidden="true" />}
    </span>
  );
}

Typewriter.propTypes = {
  text: PropTypes.string.isRequired,
};

export default Typewriter;
