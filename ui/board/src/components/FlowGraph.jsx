import PropTypes from 'prop-types';

const ROW_H = 70;
const NODE_W = 200;
const NODE_H = 44;
const CX = 150;
const WIDTH = 300;
const LANE_X = 34;
const FLOW_COLOR = '#2dd4bf';

const FILLS = {
  todo: { box: '#1c232e', edge: '#39424f' },
  done: { box: '#123b36', edge: '#0f766e' },
  current: { box: '#3d2f10', edge: '#f59e0b' },
};

function nodeTop(i) {
  return i * ROW_H + 8;
}

function edgeWordsOf(calls) {
  const words = new Map();
  calls.forEach((call) => {
    const { turns } = call;
    for (let i = 1; i < turns.length; i += 1) {
      const from = turns[i - 1].state;
      const to = turns[i].state;
      if (from !== to) {
        const key = `${from}>${to}`;
        if (!words.has(key)) words.set(key, []);
        if (turns[i].caller) words.get(key).push(turns[i].caller);
      }
    }
  });
  return words;
}

function normalize(word) {
  return word.toLowerCase().replace(/[()]/g, '').replace('pressed ', '');
}

function FlowGraph({
  states, positionId, lang, levelWord, paths, edges, calls,
}) {
  const indexOf = (id) => states.findIndex((s) => s.id === id);
  const visited = new Set();
  paths.forEach((path) => {
    path.forEach((id) => {
      if (indexOf(id) >= 0) visited.add(id);
    });
  });
  const edgeset = new Set();
  paths.forEach((path) => {
    for (let i = 1; i < path.length; i += 1) {
      const a = indexOf(path[i - 1]);
      const b = indexOf(path[i]);
      if (a >= 0 && b >= 0 && a !== b) edgeset.add(`${a}>${b}`);
    }
  });
  const words = edgeWordsOf(calls);
  const outgoing = (id) => edges.filter((e) => e.source === id);
  const taken = (edge, option) => {
    const hit = (opt) => {
      const clean = opt.trim().toLowerCase();
      if (!clean) return false;
      return (words.get(`${edge.source}>${edge.target}`) || [])
        .some((word) => normalize(word).includes(clean));
    };
    if (hit(option)) return true;
    return edge.label.split('/').some(hit); // speech is Swedish; match originals too
  };
  const pos = indexOf(positionId);
  const height = states.length * ROW_H;
  const statusOf = (id, i) => {
    if (i === pos) return 'current';
    if (visited.has(id)) return 'done';
    return 'todo';
  };
  const renderEdge = (edge) => {
    const [a, b] = edge.split('>').map(Number);
    const key = `e${edge}`;
    if (Math.abs(a - b) === 1) {
      const down = b > a;
      const y1 = down ? nodeTop(a) + NODE_H : nodeTop(a);
      const y2 = down ? nodeTop(b) : nodeTop(b) + NODE_H;
      return (
        <line
          key={key}
          x1={CX}
          y1={y1}
          x2={CX}
          y2={y2}
          stroke={FLOW_COLOR}
          strokeWidth="3"
          markerEnd="url(#farrow)"
        />
      );
    }
    const y1 = nodeTop(a) + NODE_H / 2;
    const y2 = nodeTop(b) + NODE_H / 2;
    return (
      <path
        key={key}
        d={`M ${CX} ${y1} C ${LANE_X} ${y1}, ${LANE_X} ${y2}, ${CX} ${y2}`}
        fill="none"
        stroke={FLOW_COLOR}
        strokeWidth="2"
        markerEnd="url(#farrow)"
      />
    );
  };
  return (
    <div className="flow">
      <div className="flowrow">
        <svg
          width={WIDTH}
          height={height}
          viewBox={`0 0 ${WIDTH} ${height}`}
          role="img"
          aria-label={pos >= 0 ? states[pos][lang] : levelWord}
        >
          <defs>
            <marker id="farrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
              <path d="M0,0 L6,3 L0,6 Z" fill={FLOW_COLOR} />
            </marker>
          </defs>
          <line
            x1={CX}
            y1={nodeTop(0) + NODE_H}
            x2={CX}
            y2={nodeTop(states.length - 1)}
            stroke="#39424f"
            strokeWidth="2"
          />
          {[...edgeset].map(renderEdge)}
          {states.map((state, i) => {
            const status = statusOf(state.id, i);
            const fill = FILLS[status];
            return (
              <g key={state.id} className={status === 'current' ? 'fcurrent' : undefined}>
                <rect
                  x={CX - NODE_W / 2}
                  y={nodeTop(i)}
                  width={NODE_W}
                  height={NODE_H}
                  rx="8"
                  fill={fill.box}
                  stroke={fill.edge}
                  strokeWidth="2"
                />
                <text x={CX} y={nodeTop(i) + 19} className="fname">{state[lang]}</text>
                <text x={CX} y={nodeTop(i) + 34} className="flvl">{`${levelWord} ${i + 1}`}</text>
              </g>
            );
          })}
        </svg>
        <div className="fopts">
          {states.map((state) => (
            <div key={state.id} className="fcell" style={{ height: ROW_H }}>
              {outgoing(state.id).map((edge) => (lang === 'en' && edge.label_en ? edge.label_en : edge.label).split('/').map((option) => {
                const on = taken(edge, option);
                return (
                  <div key={`${edge.target}-${option}`} className="fopt">
                    <span className={on ? 'tickbox on' : 'tickbox'} aria-hidden="true">
                      {on ? '✓' : ''}
                    </span>
                    <span>{option}</span>
                  </div>
                );
              }))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

FlowGraph.propTypes = {
  states: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
    sv: PropTypes.string.isRequired,
    en: PropTypes.string.isRequired,
  })).isRequired,
  positionId: PropTypes.string.isRequired,
  lang: PropTypes.oneOf(['sv', 'en']).isRequired,
  levelWord: PropTypes.string.isRequired,
  paths: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.string)).isRequired,
  edges: PropTypes.arrayOf(PropTypes.shape({
    source: PropTypes.string.isRequired,
    target: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
  })).isRequired,
  calls: PropTypes.arrayOf(PropTypes.shape({
    turns: PropTypes.arrayOf(PropTypes.shape({
      caller: PropTypes.string.isRequired,
      state: PropTypes.string.isRequired,
    })).isRequired,
  })).isRequired,
};

export default FlowGraph;
