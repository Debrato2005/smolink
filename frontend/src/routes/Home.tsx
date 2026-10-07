import { Link } from 'react-router';
import { ShortenPreview } from '../features/shorten/ShortenPreview';
import { Icon } from '../components/ui/Icon';
import type { ProductGateway } from '../lib/api/contracts';

function LinkSculpture() {
  return (
    <svg className="link-sculpture" viewBox="0 0 520 150" aria-hidden="true">
      <defs>
        <pattern
          id="print-dots"
          width="9"
          height="9"
          patternUnits="userSpaceOnUse"
        >
          <circle cx="2" cy="2" r="1.4" fill="currentColor" />
        </pattern>
      </defs>
      <rect x="18" y="38" width="360" height="91" fill="url(#print-dots)" />
      <path
        d="M35 24h220v56H35z"
        fill="var(--accent-blue)"
        stroke="currentColor"
        strokeWidth="3"
      />
      <path
        d="M130 67h235v54H130z"
        fill="var(--paper)"
        stroke="currentColor"
        strokeWidth="3"
      />
      <path
        d="M184 67v13h71V67"
        fill="none"
        stroke="currentColor"
        strokeWidth="3"
      />
      <path
        d="M385 53h47V26l60 48-60 48V95h-47z"
        fill="var(--accent-yellow)"
        stroke="currentColor"
        strokeWidth="3"
      />
    </svg>
  );
}
export function Home({ links }: { links: ProductGateway }) {
  return (
    <>
      <section className="hero container">
        <div className="hero-copy">
          <h1>
            Long story.
            <br />
            <span className="headline-highlight">Smol link.</span>
          </h1>
          <p className="hero-description">
            Big ideas deserve better links.
            <br />
            Shorten, personalize, and make room for what matters.
          </p>
          <LinkSculpture />
          <div className="hero-note">
            <span className="tiny-square" />
            Less link. More possibility.
          </div>
        </div>
        <ShortenPreview links={links} />
      </section>
      <div className="benefit-strip">
        <div className="container">
          <span>
            <Icon name="link" />
            Short links. Big ideas.
          </span>
          <span>
            <Icon name="qr" />
            From screen to print.
          </span>
          <span>
            <Icon name="chart" />
            Every click has a story.
          </span>
        </div>
      </div>
      <section className="feature-section container" id="features">
        <h2>
          A small link.
          <br />A lot to work with.
        </h2>
        <p className="section-intro">
          For the things you make, the places you go,
          <br className="desktop-only" /> and the ideas worth passing on.
        </p>
        <div className="feature-grid">
          <article className="feature-alias">
            <div className="feature-art alias-art" aria-hidden="true">
              <span className="mono long-label">
                your-link.com/so/many/characters
              </span>
              <Icon name="arrow" size={36} />
              <span className="mono alias-label">/your-big-idea</span>
            </div>
            <h3>Give your link a name.</h3>
            <p>
              Make it memorable with a custom alias. Keep the URL short and the
              meaning intact.
            </p>
            <span className="text-label">Custom aliases</span>
          </article>
          <article className="feature-print">
            <div className="feature-art print-art" aria-hidden="true">
              <Icon name="qr" size={80} />
              <span className="print-circle">
                <Icon name="arrow" size={42} />
              </span>
            </div>
            <h3>Made to go places.</h3>
            <p>
              Preview a QR code for your next poster, package, or calling card.
            </p>
            <span className="text-label">QR preview · Demo only</span>
          </article>
          <article className="feature-control">
            <div>
              <h3>
                Your links.
                <br />
                Your little control room.
              </h3>
              <p>
                Find a link, change its destination, or see the clicks behind
                it. Explore the workspace with sample data.
              </p>
              <Link to="/login" className="text-link">
                Explore the workspace
                <Icon name="arrow" />
              </Link>
            </div>
            <div className="control-art" aria-hidden="true">
              <div className="control-bars">
                <i />
                <i />
                <i />
                <i />
                <i />
                <i />
              </div>
              <span>Less searching. More sharing.</span>
            </div>
          </article>
        </div>
      </section>
      <section className="how-section" id="how-it-works">
        <div className="container how-grid">
          <h2>
            From a mouthful
            <br />
            to a handful.
          </h2>
          <ol>
            <li>
              <span>01</span>
              <div>
                <h3>Drop your long link.</h3>
                <p>Paste an http:// or https:// address. No account needed.</p>
              </div>
            </li>
            <li>
              <span>02</span>
              <div>
                <h3>Make it yours.</h3>
                <p>Add an alias or an expiry, if you need one.</p>
              </div>
            </li>
            <li>
              <span>03</span>
              <div>
                <h3>Copy. Then carry on.</h3>
                <p>
                  Your short URL is ready to copy. Demo links stay in this
                  preview.
                </p>
              </div>
            </li>
          </ol>
        </div>
      </section>
      <section className="faq-section container" id="questions">
        <h2>A few little answers.</h2>
        <div className="faq-list">
          {[
            [
              'Do I need an account?',
              'No. Guest link creation is the starting point. Account tools add a place to manage your links once the backend is connected.',
            ],
            [
              'What works in this preview?',
              'In demo mode, you can create sample links, preview and download QR codes, try account screens, and explore the dashboard. Changes last only until reload. Sample links do not redirect.',
            ],
            [
              'Can I choose my own link?',
              'Yes. Use an alias with 3–64 letters, numbers, or hyphens. Aliases are converted to lowercase. Reserved or existing aliases cannot be reused.',
            ],
            [
              'Can a link expire?',
              'Yes. Choose a future date and time in your local timezone. The form sends a timezone-aware expiry to the creation adapter.',
            ],
          ].map(([question, answer]) => (
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
      <section className="closing-section">
        <div className="container">
          <h2>
            Make a little
            <br />
            room for more.
          </h2>
          <a className="button-link" href="#shorten">
            Shorten a link
            <Icon name="arrow" />
          </a>
          <svg viewBox="0 0 150 150" aria-hidden="true">
            <path
              d="M75 0v150M0 75h150M22 22l106 106M22 128L128 22"
              stroke="currentColor"
              strokeWidth="24"
            />
          </svg>
        </div>
      </section>
    </>
  );
}
