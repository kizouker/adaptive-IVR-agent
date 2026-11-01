import PropTypes from 'prop-types';

function mark(entry) {
  if (entry.transfers === entry.tries) return { glyph: '✓', cls: 'kw-ok' };
  if (entry.transfers === 0) return { glyph: '✗', cls: 'kw-miss' };
  return { glyph: '~', cls: 'kw-miss' };
}

function LessonsView({ lessons, words, t }) {
  const rows = Object.entries(words)
    .map(([word, entry]) => ({ word: word === '' ? '(silence)' : word, ...entry }))
    .sort((a, b) => b.transfers - a.transfers || a.word.localeCompare(b.word));
  return (
    <>
      <ul className="lessons">
        {lessons.map((lesson) => (
          <li key={`${lesson.ts}|${lesson.persona}|${lesson.sims}`}>
            {`${lesson.ts} · ${lesson.persona} · ${lesson.sims} ${t.sims}, ${lesson.transfers} ${t.transfers}, ${lesson.served} ${t.served}, ✓${lesson.matched.length} ${t.matched}`}
          </li>
        ))}
      </ul>
      <h2>{t.learnedWords}</h2>
      <table className="words">
        <thead>
          <tr>
            <th>{t.word}</th>
            <th>{t.tries}</th>
            <th>{t.transfers}</th>
            <th aria-label="result" />
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const { glyph, cls } = mark(row);
            return (
              <tr key={row.word}>
                <td>{row.word}</td>
                <td>{row.tries}</td>
                <td>{row.transfers}</td>
                <td><span className={cls}>{glyph}</span></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </>
  );
}

LessonsView.propTypes = {
  lessons: PropTypes.arrayOf(PropTypes.shape({
    ts: PropTypes.string.isRequired,
    persona: PropTypes.string.isRequired,
    sims: PropTypes.number.isRequired,
    transfers: PropTypes.number.isRequired,
    served: PropTypes.number.isRequired,
    matched: PropTypes.arrayOf(PropTypes.string).isRequired,
  })).isRequired,
  words: PropTypes.objectOf(PropTypes.shape({
    tries: PropTypes.number.isRequired,
    transfers: PropTypes.number.isRequired,
  })).isRequired,
  t: PropTypes.shape({
    sims: PropTypes.string.isRequired,
    transfers: PropTypes.string.isRequired,
    served: PropTypes.string.isRequired,
    matched: PropTypes.string.isRequired,
    learnedWords: PropTypes.string.isRequired,
    word: PropTypes.string.isRequired,
    tries: PropTypes.string.isRequired,
  }).isRequired,
};

export default LessonsView;
