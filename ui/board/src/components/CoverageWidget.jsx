import PropTypes from 'prop-types';

function CoverageWidget({ coverage, t }) {
  const pct = coverage.total === 0
    ? 0
    : Math.round((coverage.tried / coverage.total) * 100);
  const groups = [];
  coverage.cells.forEach((cell) => {
    let group = groups.find((g) => g.name === cell.group);
    if (!group) {
      group = { name: cell.group, cells: [] };
      groups.push(group);
    }
    group.cells.push(cell);
  });
  return (
    <div className="cov">
      <div className="covpct">{`${pct}%`}</div>
      <div className="covsub">{`${coverage.tried} ${t.of} ${coverage.total} ${t.explored}`}</div>
      {groups.map((group) => (
        <div key={group.name} className="covgroup">
          <div className="covname">{group.name}</div>
          <div className="chips">
            {group.cells.map((cell) => (
              <span
                key={`${group.name}|${cell.label}`}
                className={cell.tried ? 'chip eaten' : 'chip'}
                title={`${cell.tries} ${t.tries}, ${cell.transfers} ${t.transfers}`}
              >
                {`${cell.tried ? '✓' : '•'} ${cell.label}`}
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

CoverageWidget.propTypes = {
  coverage: PropTypes.shape({
    total: PropTypes.number.isRequired,
    tried: PropTypes.number.isRequired,
    cells: PropTypes.arrayOf(PropTypes.shape({
      token: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      group: PropTypes.string.isRequired,
      tried: PropTypes.bool.isRequired,
      tries: PropTypes.number.isRequired,
      transfers: PropTypes.number.isRequired,
    })).isRequired,
  }).isRequired,
  t: PropTypes.shape({
    of: PropTypes.string.isRequired,
    explored: PropTypes.string.isRequired,
    tries: PropTypes.string.isRequired,
    transfers: PropTypes.string.isRequired,
  }).isRequired,
};

export default CoverageWidget;
