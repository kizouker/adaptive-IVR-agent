import { useState } from 'react';
import PropTypes from 'prop-types';

const MAX_DEPTH = 10;

function buildGraph(calls) {
  const next = new Map();
  const visits = new Map();
  const roots = [];
  calls.forEach((call) => {
    const { turns } = call;
    if (turns.length > 0 && !roots.includes(turns[0].state)) {
      roots.push(turns[0].state);
    }
    turns.forEach((turn) => {
      visits.set(turn.state, (visits.get(turn.state) || 0) + 1);
    });
    for (let i = 1; i < turns.length; i += 1) {
      const from = turns[i - 1].state;
      const to = turns[i].state;
      if (from !== to) {
        if (!next.has(from)) next.set(from, new Map());
        const tos = next.get(from);
        if (!tos.has(to)) tos.set(to, new Set());
        if (turns[i].caller !== '') tos.get(to).add(turns[i].caller);
      }
    }
  });
  return { next, visits, roots };
}

function TreeNode({
  id, edgeWords, states, lang, graph, positionId, seenAbove,
  branch, depth, collapsed, onToggle,
}) {
  const state = states.find((s) => s.id === id);
  const name = state ? state[lang] : id;
  const pathKey = [...branch, id].join('>');
  if (branch.includes(id)) {
    return (
      <li>
        <span className="tleaf">{`${name} (${seenAbove})`}</span>
      </li>
    );
  }
  const children = [...(graph.next.get(id) || new Map()).entries()];
  const isCurrent = id === positionId;
  const label = `${name} ×${graph.visits.get(id) || 0}`;
  if (depth >= MAX_DEPTH || children.length === 0) {
    return (
      <li>
        {edgeWords !== null && <span className="tedge">{edgeWords}</span>}
        <span className={isCurrent ? 'tnode current' : 'tnode'}>
          {label}
          {isCurrent && <span className="tdot" aria-hidden="true" />}
        </span>
      </li>
    );
  }
  const isOpen = !collapsed.has(pathKey);
  return (
    <li>
      {edgeWords !== null && <span className="tedge">{edgeWords}</span>}
      <button
        type="button"
        className="ttoggle"
        aria-expanded={isOpen}
        aria-label={name}
        onClick={() => onToggle(pathKey)}
      >
        {isOpen ? '−' : '+'}
      </button>
      <span className={isCurrent ? 'tnode current' : 'tnode'}>
        {label}
        {isCurrent && <span className="tdot" aria-hidden="true" />}
      </span>
      {isOpen && (
        <ul>
          {children.map(([to, words]) => (
            <TreeNode
              key={`${pathKey}>${to}`}
              id={to}
              edgeWords={[...words].join(', ') || null}
              states={states}
              lang={lang}
              graph={graph}
              positionId={positionId}
              seenAbove={seenAbove}
              branch={[...branch, id]}
              depth={depth + 1}
              collapsed={collapsed}
              onToggle={onToggle}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

TreeNode.propTypes = {
  id: PropTypes.string.isRequired,
  edgeWords: PropTypes.string,
  states: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
    sv: PropTypes.string.isRequired,
    en: PropTypes.string.isRequired,
  })).isRequired,
  lang: PropTypes.oneOf(['sv', 'en']).isRequired,
  graph: PropTypes.shape({
    next: PropTypes.instanceOf(Map).isRequired,
    visits: PropTypes.instanceOf(Map).isRequired,
  }).isRequired,
  positionId: PropTypes.string.isRequired,
  seenAbove: PropTypes.string.isRequired,
  branch: PropTypes.arrayOf(PropTypes.string).isRequired,
  depth: PropTypes.number.isRequired,
  collapsed: PropTypes.instanceOf(Set).isRequired,
  onToggle: PropTypes.func.isRequired,
};

TreeNode.defaultProps = {
  edgeWords: null,
};

function TreeView({
  states, calls, positionId, lang, seenAbove,
}) {
  const [collapsed, setCollapsed] = useState(() => new Set());
  const graph = buildGraph(calls);
  const onToggle = (pathKey) => {
    setCollapsed((prev) => {
      const updated = new Set(prev);
      if (updated.has(pathKey)) updated.delete(pathKey);
      else updated.add(pathKey);
      return updated;
    });
  };
  return (
    <ul className="tree">
      {graph.roots.map((root) => (
        <TreeNode
          key={root}
          id={root}
          edgeWords={null}
          states={states}
          lang={lang}
          graph={graph}
          positionId={positionId}
          seenAbove={seenAbove}
          branch={[]}
          depth={0}
          collapsed={collapsed}
          onToggle={onToggle}
        />
      ))}
    </ul>
  );
}

TreeView.propTypes = {
  states: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
    sv: PropTypes.string.isRequired,
    en: PropTypes.string.isRequired,
  })).isRequired,
  calls: PropTypes.arrayOf(PropTypes.shape({
    turns: PropTypes.arrayOf(PropTypes.shape({
      caller: PropTypes.string.isRequired,
      state: PropTypes.string.isRequired,
    })).isRequired,
  })).isRequired,
  positionId: PropTypes.string.isRequired,
  lang: PropTypes.oneOf(['sv', 'en']).isRequired,
  seenAbove: PropTypes.string.isRequired,
};

export default TreeView;
