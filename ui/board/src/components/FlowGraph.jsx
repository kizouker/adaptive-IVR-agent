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

function FlowGraph({
  states, positionId, lang, levelWord, paths,
}) {
  const indexOf = (id) => states.findIndex((s) => s.id === id);
  const visited = new Set();
  paths.forEach((path) => {
    path.forEach((id) => {
      if (indexOf(id) >= 0) visited.add(id);
    });
  });
  const edges = new Set();
  paths.forEach((path) => {
    for (let i = 1; i < path.length; i += 1) {
      const a = indexOf(path[i - 1]);
      const b = indexOf(path[i]);
      if (a >= 0 && b >= 0 && a !== b) edges.add(`${a}>${b}`);
    }
  });
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
        {[...edges].map(renderEdge)}
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
};

export default FlowGraph;
