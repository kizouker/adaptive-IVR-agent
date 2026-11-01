import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import FlowGraph from './components/FlowGraph';
import QueueWidget from './components/QueueWidget';
import TreeView from './components/TreeView';
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
    captions: 'Textning',
    queuePlace: 'Köplats',
    generated: 'Uppdaterad',
    level: 'Nivå',
    loading: 'Laddar…',
    failed: 'Kunde inte hämta data',
    overview: 'Översikt',
    details: 'Detaljer',
    tree: 'Samtalsträd',
    showAll: 'Visa alla',
    showLess: 'Visa färre',
    seenAbove: 'se ovan',
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
    captions: 'Subtitles',
    queuePlace: 'Queue place',
    generated: 'Updated',
    level: 'Level',
    loading: 'Loading…',
    failed: 'Could not fetch data',
    overview: 'Overview',
    details: 'Details',
    tree: 'Call tree',
    showAll: 'Show all',
    showLess: 'Show less',
    seenAbove: 'see above',
  },
};

const selectBoard = (state) => state.board;

function App() {
  const dispatch = useDispatch();
  const { data, lang, status } = useSelector(selectBoard);
  const [tab, setTab] = useState('overview');
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
  const queued = [...live.turns].reverse().find((turn) => turn.queue_place != null);
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
      <div className="tabs">
        <button
          type="button"
          className={tab === 'overview' ? 'on' : ''}
          onClick={() => setTab('overview')}
        >
          {t.overview}
        </button>
        <button
          type="button"
          className={tab === 'details' ? 'on' : ''}
          onClick={() => setTab('details')}
        >
          {t.details}
        </button>
      </div>
      {tab === 'overview' ? (
        <>
          <h2>{t.queuePlace}</h2>
          <QueueWidget
            place={queued?.queue_place ?? null}
            total={queued?.queue_total ?? null}
            label={t.queuePlace}
          />
          <h2>{t.process}</h2>
          <FlowGraph
            states={states}
            positionId={live.position}
            lang={lang}
            levelWord={t.level}
            paths={data.calls.map((call) => call.turns.map((turn) => turn.state))}
          />
        </>
      ) : (
        <>
          <h2>{t.tree}</h2>
          <TreeView
            states={states}
            calls={data.calls}
            positionId={live.position}
            lang={lang}
            seenAbove={t.seenAbove}
          />
          <h2>{t.calls}</h2>
          {data.calls.map((call) => (
            <CallThread key={call.persona} call={call} lang={lang} t={t} />
          ))}
        </>
      )}
    </div>
  );
}

export default App;
