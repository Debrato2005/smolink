import { useEffect, useRef, useState } from 'react';
import { Icon } from './ui/Icon';

// A moving highlights band. Screen readers get one labelled list. The
// repeated copies are decorative. Visitors can pause it (WCAG 2.2.2), it
// stops off screen, and reduced motion shows one static, wrapping list.
export function Marquee({
  items,
  label,
}: {
  items: readonly string[];
  label: string;
}) {
  const [paused, setPaused] = useState(false);
  const [offscreen, setOffscreen] = useState(false);
  const band = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const element = band.current;
    if (!element || typeof IntersectionObserver === 'undefined') return;
    const observer = new IntersectionObserver(([entry]) =>
      setOffscreen(!entry?.isIntersecting),
    );
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  const entries = items.map((item) => (
    <li key={item}>
      <StarMark />
      {item}
    </li>
  ));
  return (
    <div
      ref={band}
      className="strip marquee"
      data-paused={paused || offscreen || undefined}
    >
      <div className="marquee-window">
        <div className="marquee-track">
          <ul className="marquee-group" aria-label={label}>
            {entries}
          </ul>
          {[1, 2, 3].map((copy) => (
            <ul key={copy} className="marquee-group" aria-hidden="true">
              {entries}
            </ul>
          ))}
        </div>
      </div>
      <button
        type="button"
        className="marquee-toggle"
        aria-pressed={paused}
        aria-label={paused ? 'Play highlights' : 'Pause highlights'}
        onClick={() => setPaused(!paused)}
      >
        <Icon name={paused ? 'play' : 'pause'} size={16} />
      </button>
    </div>
  );
}

export function StarMark({ className = 'star-mark' }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M12 1.5l2.6 7.1 7.4.4-5.8 4.7 2 7.3L12 16.8 5.8 21l2-7.3L2 9l7.4-.4z" />
    </svg>
  );
}
