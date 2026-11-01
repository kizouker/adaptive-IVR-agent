/* eslint-disable no-await-in-loop -- scripted conversation: turns are
   deliberately sequential, never parallelizable. */
import { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import { dtmf, speechVolume } from '../audio';

const STEP_MS = 1100;
const QUEUE_MS = 1400;

function wait(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

function reducedMotion() {
  return typeof window !== 'undefined'
    && typeof window.matchMedia === 'function'
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function speak(text, lang) {
  try {
    if (typeof window === 'undefined' || !window.speechSynthesis || !text) {
      return;
    }
    const synth = window.speechSynthesis;
    synth.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = lang === 'en' ? 'en-US' : 'sv-SE';
    utter.volume = speechVolume();
    const prefix = lang === 'en' ? 'en' : 'sv';
    const voice = synth.getVoices().find((v) => v.lang && v.lang.startsWith(prefix));
    if (voice) {
      utter.voice = voice;
    }
    synth.speak(utter);
  } catch {
    // Silent terminal is still a working terminal.
  }
}

function stopSpeech() {
  try {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
  } catch {
    // Nothing to stop.
  }
}

function normalize(value) {
  return value.trim().toLowerCase();
}

// Real robot flow, driven by baked line IDs: open question, no-match ladder,
// yes/no, handover, identification, queue, officer.
function TerminalModal({
  lines, words, lang, t, onClose,
}) {
  const [turns, setTurns] = useState([]);
  const [value, setValue] = useState('');
  const [live, setLive] = useState(true);
  const [runId, setRunId] = useState(0);
  const boxRef = useRef(null);
  const inputRef = useRef(null);
  const answerRef = useRef(null);
  const [fetched, setFetched] = useState(null);
  const ready = lines.length > 0 ? lines : fetched;
  const [listening, setListening] = useState(false);
  const recRef = useRef(null);
  const canMic = typeof window !== 'undefined'
    && (window.SpeechRecognition || window.webkitSpeechRecognition);

  const stopMic = () => {
    try {
      if (recRef.current) {
        recRef.current.stop();
        recRef.current = null;
      }
    } catch {
      // Already stopped.
    }
    setListening(false);
  };

  const toggleMic = () => {
    if (!canMic) {
      return;
    }
    if (listening) {
      stopMic();
      return;
    }
    try {
      const Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
      const rec = new Rec();
      rec.lang = 'sv-SE';
      rec.interimResults = false;
      rec.onresult = (event) => {
        const said = event.results[0][0].transcript;
        if (answerRef.current) {
          const resolve = answerRef.current;
          answerRef.current = null;
          resolve(said);
          setValue('');
        } else {
          setValue(said);
        }
      };
      rec.onend = () => {
        recRef.current = null;
        setListening(false);
      };
      rec.onerror = () => {
        recRef.current = null;
        setListening(false);
      };
      recRef.current = rec;
      rec.start();
      setListening(true);
    } catch {
      setListening(false);
    }
  };

  const byId = {};
  (ready ?? []).forEach((line) => {
    byId[line.id] = line;
  });
  const text = (id) => {
    const line = byId[id];
    if (!line) {
      return '';
    }
    if (lang === 'en' && line.en) {
      return line.en;
    }
    return line.text;
  };
  const transferWords = Object.keys(words).filter((word) => words[word].transfers > 0);
  const matched = (said) => {
    const clean = normalize(said);
    if (!clean) {
      return null;
    }
    return transferWords.find((word) => {
      const w = word.toLowerCase();
      return clean === w || clean.includes(w) || (w.length > 3 && w.includes(clean));
    }) ?? null;
  };

  const say = async (id, voice) => {
    const line = text(id);
    setTurns((prev) => [...prev, { who: 'agda', text: line }]);
    speak(line, voice);
    await wait(reducedMotion() ? 80 : STEP_MS);
  };

  const ask = () => new Promise((resolve) => {
    answerRef.current = resolve;
  });

  const hear = async () => {
    const said = await ask();
    if (/^[0-9*#]$/.test(said.trim())) {
      dtmf(said.trim());
    }
    const shown = said.trim() === '' ? t.terminalSilence : said;
    setTurns((prev) => [...prev, { who: 'you', text: shown }]);
    return said;
  };

  useEffect(() => {
    let liveFetch = true;
    if (lines.length === 0 && fetched === null) {
      fetch('doorkeeper-lines.json')
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => {
          if (liveFetch) {
            setFetched(data && data.lines ? data.lines : []);
          }
        })
        .catch(() => {
          if (liveFetch) {
            setFetched([]);
          }
        });
    }
    return () => {
      liveFetch = false;
    };
  }, [lines, fetched]);

  useEffect(() => {
    let cancelled = false;
    if (!ready || ready.length === 0) {
      return () => {
        cancelled = true;
      };
    }
    const run = async () => {
      // eslint-disable-next-line no-use-before-define
      const check = () => !cancelled;
      const busyDay = Math.random() < 0.25;
      await say(busyDay ? 'L44' : 'L01', 'sv');
      if (!check()) return;
      const first = normalize(await hear());
      if (!check()) return;
      if (first === '0') {
        await say('L17', 'en');
        if (!check()) return;
        await say('L18', 'en');
        if (!check()) return;
        await hear();
        if (!check()) return;
        await say('L37', 'en');
        if (!check()) return;
        await say('L40', 'en');
        setLive(false);
        return;
      }
      let said = first;
      const ladder = ['L02', 'L03', 'L04', 'L05', 'L21'];
      let word = null;
      for (let i = 0; i < ladder.length && !word && check(); i += 1) {
        if (i > 0 || said === '') {
          if (i > 0) {
            await say(ladder[i], 'sv');
            if (!check()) return;
          }
        } else {
          await say(ladder[0], 'sv');
          if (!check()) return;
        }
        if (i === 0 && said !== '') {
          word = matched(said);
        } else {
          const reply = await hear();
          if (!check()) return;
          said = normalize(reply);
          word = matched(said);
        }
      }
      if (!check()) return;
      if (!word) {
        let answer = '';
        for (let i = 0; i < 3 && !answer && check(); i += 1) {
          await say(i === 0 ? 'L22' : 'L41', 'sv');
          if (!check()) return;
          const reply = normalize(await hear());
          if (!check()) return;
          if (['ja', 'j', 'yes', 'y', 'nej', 'n', 'no'].includes(reply)) {
            answer = reply;
          }
        }
      }
      if (!check()) return;
      await say('L19', 'sv');
      if (!check()) return;
      await say('L43', 'sv');
      if (!check()) return;
      let idOk = false;
      for (let i = 0; i < 3 && !idOk && check(); i += 1) {
        await say(i === 0 ? 'L09' : 'L10', 'sv');
        if (!check()) return;
        const reply = normalize(await hear());
        if (!check()) return;
        if (reply === '1' || reply === '2') {
          idOk = true;
        }
      }
      if (!check()) return;
      await say(idOk ? 'L11' : 'L12', 'sv');
      if (!check() || !idOk) {
        setLive(false);
        return;
      }
      await say('L13', 'sv');
      if (!check()) return;
      for (let n = 3; n >= 1 && check(); n -= 1) {
        const line = text('L29').replace('1', String(n));
        setTurns((prev) => [...prev, { who: 'agda', text: line }]);
        speak(line, 'sv');
        await wait(reducedMotion() ? 80 : QUEUE_MS);
      }
      if (!check()) return;
      await say('L30', 'sv');
      if (!check()) return;
      await say('L15', 'sv');
      if (!check()) return;
      const survey = normalize(await hear());
      if (!check()) return;
      if (survey === '1') {
        await say('L16', 'sv');
        if (!check()) return;
      }
      await say('L39', 'sv');
      setLive(false);
    };
    run();
    return () => {
      cancelled = true;
      stopSpeech();
      stopMic();
      if (answerRef.current) {
        answerRef.current('');
        answerRef.current = null;
      }
    };
  }, [runId, ready?.length]);

  useEffect(() => {
    const onKey = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => {
      window.removeEventListener('keydown', onKey);
    };
  }, [onClose]);

  useEffect(() => {
    if (boxRef.current) {
      boxRef.current.scrollTop = boxRef.current.scrollHeight;
    }
    if (inputRef.current && live) {
      inputRef.current.focus();
    }
  }, [turns, live]);

  const submit = (event) => {
    event.preventDefault();
    if (answerRef.current) {
      const resolve = answerRef.current;
      answerRef.current = null;
      resolve(value);
      setValue('');
    }
  };

  const restart = () => {
    stopSpeech();
    stopMic();
    if (answerRef.current) {
      answerRef.current('');
      answerRef.current = null;
    }
    setTurns([]);
    setValue('');
    setLive(true);
    setRunId((n) => n + 1);
  };

  const renderInput = () => {
    if (!live) {
      return <p className="tend">{t.terminalEnd}</p>;
    }
    if (ready === null) {
      return <p className="thint">{t.loading}</p>;
    }
    return (
      <form onSubmit={submit} className="tform">
        <span aria-hidden="true">&gt;</span>
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder={t.terminalPlaceholder}
          aria-label={t.terminalPlaceholder}
          autoComplete="off"
        />
        {canMic && (
          <button type="button" className="tbtn" onClick={toggleMic} aria-label={t.terminalMic}>
            {listening ? t.terminalListening : t.terminalMic}
          </button>
        )}
      </form>
    );
  };

  if (ready !== null && ready.length === 0) {
    return (
      <div className="tmodal" role="dialog" aria-modal="true" aria-label={t.terminalTitle}>
        <div className="tbody">
          <div className="thead">
            <strong>{t.terminalTitle}</strong>
            <span className="spacer" />
            <button type="button" className="tbtn" onClick={onClose} aria-label={t.terminalClose}>
              ✕
            </button>
          </div>
          <p className="thint">{t.failed}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="tmodal" role="dialog" aria-modal="true" aria-label={t.terminalTitle}>
      <div className="tbody" ref={boxRef}>
        <div className="thead">
          <strong>{t.terminalTitle}</strong>
          <span className="tsim">{t.terminalSim}</span>
          <span className="spacer" />
          <button type="button" className="tbtn" onClick={restart}>
            {t.terminalRestart}
          </button>
          <button type="button" className="tbtn" onClick={onClose} aria-label={t.terminalClose}>
            ✕
          </button>
        </div>
        <p className="thint">{t.terminalHint}</p>
        {turns.map((turn, i) => (
          // eslint-disable-next-line react/no-array-index-key -- turns only append
          <p key={`${i}-${turn.who}`} className={turn.who === 'agda' ? 't-agda' : 't-you'}>
            <strong>{turn.who === 'agda' ? 'AGDA' : 'YOU'}</strong>
            {' '}
            {turn.text}
          </p>
        ))}
        {renderInput()}
      </div>
    </div>
  );
}

TerminalModal.propTypes = {
  lines: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
    text: PropTypes.string.isRequired,
    en: PropTypes.string,
  })).isRequired,
  words: PropTypes.objectOf(PropTypes.shape({
    tries: PropTypes.number,
    transfers: PropTypes.number,
  })).isRequired,
  lang: PropTypes.string.isRequired,
  t: PropTypes.shape({
    failed: PropTypes.string.isRequired,
    loading: PropTypes.string.isRequired,
    terminalTitle: PropTypes.string.isRequired,
    terminalSim: PropTypes.string.isRequired,
    terminalHint: PropTypes.string.isRequired,
    terminalPlaceholder: PropTypes.string.isRequired,
    terminalSilence: PropTypes.string.isRequired,
    terminalRestart: PropTypes.string.isRequired,
    terminalClose: PropTypes.string.isRequired,
    terminalEnd: PropTypes.string.isRequired,
    terminalMic: PropTypes.string.isRequired,
    terminalListening: PropTypes.string.isRequired,
  }).isRequired,
  onClose: PropTypes.func.isRequired,
};

export default TerminalModal;
