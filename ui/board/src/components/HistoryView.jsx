const TIMELINE = [
  {
    year: '1939',
    text: 'Bell Labs demonstrates the VODER, the first machine to produce intelligible speech. An operator plays it like an organ.',
  },
  {
    year: '1961',
    text: 'An IBM 704 at Bell Labs sings "Daisy Bell" — the first song performed entirely by a computer.',
  },
  {
    year: '1970s',
    text: 'Touch-tone (DTMF) phones spread, and the first automated phone menus appear in US banks and airlines.',
  },
  {
    year: '1984',
    text: 'DECtalk brings formant synthesis to a box on a desk. Its voice later becomes famous as Stephen Hawking\u2019s.',
  },
  {
    year: '1990s',
    text: 'Speech recognition reaches call centers, and concatenative synthesis makes robot voices far more natural. Sweden gets "talsvar" at banks, Telia, and SJ.',
  },
  {
    year: '2000',
    text: 'VoiceXML 1.0 gives IVR menus a web-like standard, and outsourcing makes phone robots the default front door.',
  },
  {
    year: '2000s',
    text: 'Swedish agencies automate routine errands: long DTMF menus and keyword spotting at Försäkringskassan, Skatteverket, and Arbetsförmedlingen.',
  },
  {
    year: '2011',
    text: 'Siri puts a voice assistant in every pocket and normalizes talking to machines.',
  },
  {
    year: '2016',
    text: 'DeepMind\u2019s WaveNet makes neural text-to-speech sound almost human. Two years later Google Duplex books a haircut over the phone.',
  },
  {
    year: '2020s',
    text: 'LLM voicebots arrive. Swedish agencies pilot AI receptionists while BankID keeps a human in the loop for identity.',
  },
  {
    year: '2026',
    text: 'This project: instead of teaching humans the magic words, an agent learns the menus and waits in line for you.',
  },
];

const SUSPECTED = [
  'Contact-center platforms such as Cisco or Genesys behind the 0771 numbers, with DTMF menus on top.',
  'Speech recognition from vendors like Nuance in some lines; keyword spotting rather than real understanding in most.',
  'Newer Swedish and Nordic voicebot vendors piloting LLM receptionists at a few agencies.',
  'Exact-word matching everywhere: say the wrong synonym and the robot loops "please answer yes or no". Our transcripts back this one.',
];

function HistoryView() {
  return (
    <div className="hist">
      <h2>How phone robots took over Sweden</h2>
      <p>
        A short history of speech synthesis and IVR menus, and what we believe
        Swedish agencies run today. Corrections welcome — see the bottom.
      </p>
      <ol className="timeline">
        {TIMELINE.map((item) => (
          <li key={item.year}>
            <strong>{item.year}</strong>
            <span>{item.text}</span>
          </li>
        ))}
      </ol>
      <h2>What agencies seem to run today (unconfirmed)</h2>
      <p>
        Vendors rarely say which agency runs what, so this is our best guess
        from public sources and recorded calls:
      </p>
      <ul>
        {SUSPECTED.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      <h2>Worked on one of these systems?</h2>
      <p>
        Tell us what stack it really was — vendor, platform, speech engine —
        so we can confirm or correct the list above.
        {' '}
        <a href="https://github.com/kizouker/adaptive-IVR-agent/issues">Open an issue</a>
        {' '}
        and we will update this page.
      </p>
    </div>
  );
}

export default HistoryView;
