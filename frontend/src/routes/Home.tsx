import { ShortenPreview } from '../features/shorten/ShortenPreview';
import { Icon } from '../components/ui/Icon';
import { HeroBackdrop, HeroLinkExample } from '../components/HeroArtwork';
import { Marquee, StarMark } from '../components/Marquee';
import type { ProductGateway } from '../lib/api/contracts';

const highlights = [
  'No sign-up',
  'Custom aliases',
  'Link expiry',
  'One-click copy',
  'Works on any device',
] as const;

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

const steps = [
  ['Paste', 'Drop any http:// or https:// link into the box.'],
  ['Personalize', 'Add an alias or an expiry, if you want one.'],
  ['Share', 'Copy your short link and send it anywhere.'],
] as const;

// A dashed "cut here" rule with scissors. The page's recurring motif.
function CutLine() {
  return (
    <div className="cut-line" aria-hidden="true">
      <Icon name="scissors" size={26} />
    </div>
  );
}

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
      <div className="home-intro">
        <section className="hero" aria-labelledby="hero-heading">
          <div className="container hero-inner">
            <div className="hero-copy">
              <span className="hero-eyebrow">Less URL. More you.</span>
              <h1 id="hero-heading" className="display">
                Long links?
                <span className="hero-highlight">Smol it.</span>
              </h1>
              <p className="hero-lede">
                Paste a long URL, get a smol link in seconds.
                <span>No sign-up needed. Just shorten and share.</span>
              </p>
              <HeroLinkExample />
            </div>
            <div className="hero-shortener">
              <HeroBackdrop />
              <ShortenPreview links={links} />
            </div>
          </div>
        </section>

        <Marquee items={highlights} label="Highlights" />
      </div>

      <section
        className="features container"
        id="features"
        aria-labelledby="features-heading"
      >
        <div className="section-heading">
          <h2 id="features-heading">Small links. Big features.</h2>
          <p className="section-lede">
            Everything a link needs to travel well. Nothing it does not.
          </p>
        </div>
        <div className="feature-grid">
          {features.map((feature) => (
            <article
              key={feature.title}
              className={`feature-card tone-${feature.tone}`}
            >
              <span className="feature-icon">
                <Icon name={feature.icon} size={28} />
              </span>
              <h3>{feature.title}</h3>
              <p>{feature.text}</p>
              {'soon' in feature && feature.soon && (
                <span className="badge sticker-badge">Coming soon</span>
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
        <div className="section-heading">
          <h2 id="steps-heading">How it works</h2>
          <p className="section-lede">Three moves. No detours.</p>
        </div>
        <ol className="step-list">
          {steps.map(([title, text]) => (
            <li key={title}>
              <h3>{title}</h3>
              <p>{text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section
        className="faq container"
        id="questions"
        aria-labelledby="faq-heading"
      >
        <div className="faq-intro">
          <h2 id="faq-heading">Questions</h2>
          <p className="section-lede">Smol answers to common questions.</p>
          <span className="faq-mark" aria-hidden="true">
            ?
          </span>
        </div>
        <div className="faq-list">
          {questions.map(([question, answer]) => (
            <details key={question}>
              <summary>
                {question}
                <span className="faq-toggle" aria-hidden="true">
                  <Icon name="plus" />
                </span>
              </summary>
              <p>{answer}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="closing" aria-labelledby="closing-heading">
        <CutLine />
        <div className="container closing-inner">
          <h2 id="closing-heading">
            Got a long one?
            <StarMark className="closing-star" />
          </h2>
          <a className="button-link" href="#shorten">
            Shorten it now
            <Icon name="arrow" />
          </a>
        </div>
      </section>
    </>
  );
}
