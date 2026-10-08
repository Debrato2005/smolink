import { ShortenPreview } from '../features/shorten/ShortenPreview';
import { Icon } from '../components/ui/Icon';
import type { ProductGateway } from '../lib/api/contracts';

const highlights = [
  'No sign-up',
  'Custom aliases',
  'Link expiry',
  'One-click copy',
  'Works on any device',
];

const questions = [
  [
    'Do I need an account?',
    'No. Paste a link and shorten it right away. An account adds one place to find, edit, and measure your links.',
  ],
  [
    'Can I choose my own link?',
    'Yes. Use an alias with 3–64 letters, numbers, or hyphens. Smolink saves it in lowercase. Reserved and taken aliases are refused.',
  ],
  [
    'Can a link expire?',
    'Yes. Choose a future date and time. The form uses your timezone and saves the exact moment.',
  ],
] as const;

export function Home({ links }: { links: ProductGateway }) {
  // Production marks features whose backend service does not exist yet.
  const soon = links.source === 'live';
  const features = [
    {
      icon: 'link',
      tone: 'yellow',
      title: 'Your words, your link',
      text: 'Pick an alias people remember, like /launch-kit, or let Smolink choose a short code.',
    },
    {
      icon: 'clock',
      tone: 'coral',
      title: 'Links that expire',
      text: 'Set a date and time. After that moment, the link stops working.',
    },
    {
      icon: 'qr',
      tone: 'blue',
      title: 'QR codes for print',
      text: 'Download a crisp PNG for posters, packaging, and slides.',
      soon,
    },
    {
      icon: 'chart',
      tone: 'green',
      title: 'Clicks you can read',
      text: 'Daily counts, sources, and devices for every link you own.',
      soon,
    },
  ] as const;
  return (
    <>
      <section className="hero" aria-labelledby="hero-heading">
        <div className="container hero-inner">
          <h1 id="hero-heading" className="display">
            Long story. <span className="pop">Smol</span> link.
          </h1>
          <p className="hero-lede">
            Paste a long link. Get a short one you can share, print, or say out
            loud.
          </p>
          <ShortenPreview links={links} />
        </div>
      </section>

      <ul className="strip" aria-label="Highlights">
        {highlights.map((item) => (
          <li key={item}>
            <Icon name="spark" size={18} />
            {item}
          </li>
        ))}
      </ul>

      <section
        className="features container"
        id="features"
        aria-labelledby="features-heading"
      >
        <h2 id="features-heading">Small links. Big features.</h2>
        <div className="feature-grid">
          {features.map((feature) => (
            <article
              key={feature.title}
              className={`feature-card tone-${feature.tone}`}
            >
              <span className="feature-icon">
                <Icon name={feature.icon} size={26} />
              </span>
              <h3>{feature.title}</h3>
              <p>{feature.text}</p>
              {'soon' in feature && feature.soon && (
                <span className="badge">Coming soon</span>
              )}
            </article>
          ))}
        </div>
      </section>

      <section
        className="steps container"
        id="how-it-works"
        aria-labelledby="steps-heading"
      >
        <h2 id="steps-heading">How it works</h2>
        <ol className="step-list">
          <li>
            <h3>Paste</h3>
            <p>Drop any http:// or https:// link into the box.</p>
          </li>
          <li>
            <h3>Personalize</h3>
            <p>Add an alias or an expiry, if you want one.</p>
          </li>
          <li>
            <h3>Share</h3>
            <p>Copy your short link and send it anywhere.</p>
          </li>
        </ol>
      </section>

      <section
        className="faq container"
        id="questions"
        aria-labelledby="faq-heading"
      >
        <h2 id="faq-heading">Questions</h2>
        <div className="faq-list">
          {questions.map(([question, answer]) => (
            <details key={question}>
              <summary>
                {question}
                <Icon name="plus" />
              </summary>
              <p>{answer}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="closing" aria-labelledby="closing-heading">
        <div className="container closing-inner">
          <h2 id="closing-heading">Got a long one?</h2>
          <a className="button-link" href="#shorten">
            Shorten it now
            <Icon name="arrow" />
          </a>
        </div>
      </section>
    </>
  );
}
