import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import FlowGraph from './components/FlowGraph';
import QueueWidget from './components/QueueWidget';
import TreeView from './components/TreeView';
import CallThread from './components/CallThread';
import Subtitle from './components/Subtitle';
import VolumeWidget from './components/VolumeWidget';
import CIWidget from './components/CIWidget';
import LessonsView from './components/LessonsView';
import KeypadWidget from './components/KeypadWidget';
import CoverageWidget from './components/CoverageWidget';
import HistoryView from './components/HistoryView';
import TerminalModal from './components/TerminalModal';
import PacmanView from './components/PacmanView';
import { fetchBoard, setLang } from './store/boardSlice';

const POLL_MS = 3000;

const STRINGS = {
  sv: {
    title: 'Holdmate-board',
    live: 'exempeldata',
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
    keypad: 'Knappsats',
    generated: 'Uppdaterad',
    volume: 'Volym',
    quieter: 'Sänk',
    louder: 'Höj',
    browser: 'webbläsare',
    builds: 'Byggen',
    allBuilds: 'alla →',
    level: 'Nivå',
    loading: 'Laddar…',
    failed: 'Kunde inte hämta data',
    overview: 'Översikt',
    details: 'Detaljer',
    lessons: 'Lektioner',
    historyTab: 'Historia',
    maze: 'Labyrint',
    lessonsRun: 'Körda lektioner',
    noLessons: 'Kör lektioner från menyn (4 → 1) för att fylla denna flik.',
    coverage: 'Täckning',
    of: 'av',
    explored: 'avsökt',
    hintWord: 'Ord HoldMate prövat',
    hintTries: 'Så många gånger ordet prövats',
    hintTransfers: 'Så många gånger ordet ledde till koppling (förstått)',
    hintResult: '✓ kopplar alltid, ~ ibland, ✗ aldrig',
    hintCoverage: 'Andel prövade menuval (simulerade, ej nödvändigtvis inlärda)',
    learnedWords: 'Inlärda ord',
    sims: 'simuleringar',
    transfers: 'kopplingar',
    served: 'framme',
    matched: 'träffar',
    word: 'Ord',
    tries: 'Försök',
    tree: 'Samtalsträd',
    treeStates: 'Tillstånd',
    treeAnswers: 'Svar',
    now: 'Just nu',
    history: 'Historik',
    showLess: 'Visa färre',
    seenAbove: 'se ovan',
    tryCli: 'Prova CLI:t',
    terminalTitle: 'Holdmate CLI (simulerat)',
    terminalSim: 'simulering',
    terminalHint: 'Skriv svar som i tyst läge. 0 ger engelska menyn, 1/2 identifierar, tom rad är tystnad.',
    terminalPlaceholder: 'Skriv ditt svar…',
    terminalSilence: '(tystnad)',
    terminalRestart: 'Börja om',
    terminalClose: 'Stäng',
    terminalEnd: 'Demosamtalet är slut — börja om eller stäng med Esc.',
  },
  en: {
    title: 'Holdmate board',
    live: 'sample data',
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
    keypad: 'Keypad',
    generated: 'Updated',
    volume: 'Volume',
    quieter: 'Quieter',
    louder: 'Louder',
    browser: 'browser',
    builds: 'Builds',
    allBuilds: 'all →',
    level: 'Level',
    loading: 'Loading…',
    failed: 'Could not fetch data',
    overview: 'Overview',
    details: 'Details',
    lessons: 'Lessons',
    historyTab: 'History',
    maze: 'Maze',
    lessonsRun: 'Lessons run',
    noLessons: 'Run lessons from the menu (4 → 1) to fill this tab.',
    coverage: 'Coverage',
    of: 'of',
    explored: 'explored',
    hintWord: 'Word HoldMate tried',
    hintTries: 'How many times the word was tried',
    hintTransfers: 'How many times the word led to a transfer (understood)',
    hintResult: '✓ always transfers, ~ sometimes, ✗ never',
    hintCoverage: 'Share of menu options tried (simulated, not necessarily learned)',
    learnedWords: 'Learned words',
    sims: 'sims',
    transfers: 'transfers',
    served: 'served',
    matched: 'matched',
    word: 'Word',
    tries: 'Tries',
    tree: 'Call tree',
    treeStates: 'States',
    treeAnswers: 'Answers',
    now: 'Right now',
    history: 'History',
    showLess: 'Show less',
    seenAbove: 'see above',
    tryCli: 'Try the CLI',
    terminalTitle: 'Holdmate CLI (simulated)',
    terminalSim: 'simulation',
    terminalHint: 'Type answers as in quiet mode. 0 gives the English menu, 1/2 identify, empty line is silence.',
    terminalPlaceholder: 'Type your answer…',
    terminalSilence: '(silence)',
    terminalRestart: 'Restart',
    terminalClose: 'Close',
    terminalEnd: 'Demo call over — restart or close with Esc.',
  },
};

const selectBoard = (state) => state.board;

function App() {
  const dispatch = useDispatch();
  const { data, lang, status } = useSelector(selectBoard);
  const [tab, setTab] = useState('overview');
  const [treeMode, setTreeMode] = useState('states');
  const [version, setVersion] = useState(null);
  const [showTerminal, setShowTerminal] = useState(false);

  useEffect(() => {
    fetch('version.json').then((res) => {
      if (res.ok) return res.json();
      throw new Error('no version file');
    }).then((info) => {
      setVersion(info.version);
    }).catch(() => {
      // Dev server without version plugin or stale deploy: hide it.
    });
  }, []);
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
  const latest = live.turns.length === 0 ? null : live.turns[live.turns.length - 1];
  const latestSv = latest == null ? null : latest.robot;
  const latestEn = latest == null ? null : (latest.robot_en ?? latest.robot);
  const latestRobot = lang === 'en' ? latestEn : latestSv;
  const subtitleKey = latest == null
    ? `${live.persona}|none`
    : latest.caller_audio || `${latest.caller}|${latest.robot}`;
  return (
    <div className="wrap">
      <div className="top">
        <h1>{t.title}</h1>
        <span className="live">
          <span className="dot" />
          {t.live}
        </span>
        {version != null && <span className="ver">{version}</span>}
        <span className="spacer" />
        <button type="button" className="tbtn" onClick={() => setShowTerminal(true)}>
          {t.tryCli}
        </button>
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
      <VolumeWidget label={t.volume} quieter={t.quieter} louder={t.louder} browser={t.browser} />
      <CIWidget label={t.builds} all={t.allBuilds} />
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
        <button
          type="button"
          className={tab === 'lessons' ? 'on' : ''}
          onClick={() => setTab('lessons')}
        >
          {t.lessons}
        </button>
        <button
          type="button"
          className={tab === 'history' ? 'on' : ''}
          onClick={() => setTab('history')}
        >
          {t.historyTab}
        </button>
        <button
          type="button"
          className={tab === 'maze' ? 'on' : ''}
          onClick={() => setTab('maze')}
        >
          {t.maze}
        </button>
      </div>
      {tab === 'overview' && (
        <div className="ovrow">
          <div className="ovflow">
            <h2>{t.process}</h2>
            <FlowGraph
              states={states}
              positionId={live.position}
              lang={lang}
              levelWord={t.level}
              paths={data.calls.map((call) => call.turns.map((turn) => turn.state))}
              edges={data.maps[live.map].edges ?? []}
              calls={data.calls}
            />
          </div>
          <div className="ovqueue">
            <h2>{t.queuePlace}</h2>
            <QueueWidget
              place={queued?.queue_place ?? null}
              total={queued?.queue_total ?? null}
              label={t.queuePlace}
            />
            <h2>{t.keypad}</h2>
            <KeypadWidget label={t.keypad} />
          </div>
        </div>
      )}
      {tab === 'details' && (
        <>
          <h2>{t.now}</h2>
          <Subtitle
            key={subtitleKey}
            text={latestRobot}
            who={(latest && latest.speaker) || live.robot_name || t.robot}
          />
          <h2>{t.tree}</h2>
          <div className="tabs">
            <button
              type="button"
              className={treeMode === 'states' ? 'on' : ''}
              onClick={() => setTreeMode('states')}
            >
              {t.treeStates}
            </button>
            <button
              type="button"
              className={treeMode === 'answers' ? 'on' : ''}
              onClick={() => setTreeMode('answers')}
            >
              {t.treeAnswers}
            </button>
          </div>
          <TreeView
            states={states}
            calls={data.calls}
            positionId={live.position}
            lang={lang}
            seenAbove={t.seenAbove}
            byAnswer={treeMode === 'answers'}
          />
          <h2>{t.calls}</h2>
          {data.calls.map((call) => (
            <CallThread key={call.persona} call={call} lang={lang} t={t} />
          ))}
        </>
      )}
      {tab === 'lessons' && (
        <>
          <h2>{t.coverage}</h2>
          {data.coverage != null && <CoverageWidget coverage={data.coverage} t={t} />}
          <h2>{t.lessonsRun}</h2>
          <LessonsView
            lessons={data.lessons ?? []}
            words={data.words ?? {}}
            t={t}
          />
        </>
      )}
      {tab === 'history' && <HistoryView />}
      {tab === 'maze' && (
        <>
          <h2>{t.maze}</h2>
          <PacmanView calls={data.calls} t={t} />
        </>
      )}
      {showTerminal && (
        <TerminalModal
          lines={data.lines ?? []}
          words={data.words ?? {}}
          lang={lang}
          t={t}
          onClose={() => setShowTerminal(false)}
        />
      )}
    </div>
  );
}

export default App;
