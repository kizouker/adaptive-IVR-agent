import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import ProcessHeader from './components/ProcessHeader';
import CallThread from './components/CallThread';
import { fetchBoard, setLang } from './store/boardSlice';

const POLL_MS = 3000;

const STRINGS = {
  sv: {
    title: 'Holdmate liveboard',
    live: 'live',
    process: 'Processen',
    calls: 'Samtalen',
    errand: 'Ärende',
    state: 'Steg',
    routed: 'styrt mot ärendet',
    missed: 'uppfattades inte',
    caller: 'Uppringare (Oskar)',
    robot: 'AF Agda (Alva)',
    generated: 'Uppdaterad',
    level: 'Nivå',
    loading: 'Laddar…',
    failed: 'Kunde inte hämta data',
  },
  en: {
    title: 'Holdmate live board',
    live: 'live',
    process: 'The process',
    calls: 'The calls',
    errand: 'Errand',
    state: 'Step',
    routed: 'routed to errand',
    missed: 'not understood',
    caller: 'Caller (Oskar)',
    robot: 'AF Agda (Alva)',
    generated: 'Updated',
    level: 'Level',
    loading: 'Loading…',
    failed: 'Could not fetch data',
  },
};

const selectBoard = (state) => state.board;

function App() {
  const dispatch = useDispatch();
  const { data, lang, status } = useSelector(selectBoard);
  const t = STRINGS[lang];

  useEffect(() => {
    dispatch(fetchBoard());
    const id = setInterval(() => {
      dispatch(fetchBoard());
    }, POLL_MS);
    return () => {
      clearInterval(id);
    };
  }, [dispatch]);

  if (!data) {
    return (
      <div className="wrap">
        <p>{status === 'failed' ? t.failed : t.loading}</p>
      </div>
    );
  }
  const live = data.calls[data.calls.length - 1];
  const { states } = data.maps[live.map];
  return (
    <div className="wrap">
      <div className="top">
        <h1>{t.title}</h1>
        <span className="live">
          <span className="dot" />
          {t.live}
        </span>
        <span className="spacer" />
        <span className="lang">
          <button type="button" className={lang === 'sv' ? 'on' : ''} onClick={() => dispatch(setLang('sv'))}>
            SV
          </button>
          <button type="button" className={lang === 'en' ? 'on' : ''} onClick={() => dispatch(setLang('en'))}>
            EN
          </button>
        </span>
      </div>
      <div className="sub">{`${t.generated} ${data.generated}`}</div>
      <h2>{t.process}</h2>
      <ProcessHeader states={states} positionId={live.position} lang={lang} levelWord={t.level} />
      <h2>{t.calls}</h2>
      {data.calls.map((call) => (
        <CallThread key={call.persona} call={call} lang={lang} t={t} />
      ))}
    </div>
  );
}

export default App;
