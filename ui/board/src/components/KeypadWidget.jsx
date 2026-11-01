import { useState } from 'react';
import PropTypes from 'prop-types';
import { dtmf } from '../audio';

const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#'];

async function sendDigit(key) {
  try {
    await fetch('/api/dtmf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ digit: key }),
    });
  } catch {
    // Static site (Pages): local beep only, nothing listens.
  }
}

function KeypadWidget({ label }) {
  const [last, setLast] = useState(null);
  const press = (key) => {
    dtmf(key);
    setLast(key);
    sendDigit(key);
  };
  return (
    <div className="keypad" role="group" aria-label={label}>
      {KEYS.map((key) => (
        <button
          key={key}
          type="button"
          className={key === last ? 'kkey hit' : 'kkey'}
          onClick={() => press(key)}
          aria-label={key}
        >
          {key}
        </button>
      ))}
    </div>
  );
}

KeypadWidget.propTypes = {
  label: PropTypes.string.isRequired,
};

export default KeypadWidget;
