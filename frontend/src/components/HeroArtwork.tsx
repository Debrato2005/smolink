import type { ReactNode } from 'react';
import { Icon } from './ui/Icon';

export function HeroBackdrop() {
  return (
    <>
      <svg
        className="hero-backdrop"
        viewBox="0 0 1536 1024"
        preserveAspectRatio="none"
        aria-hidden="true"
        focusable="false"
      >
        <ellipse
          className="hero-backdrop-fill"
          cx="768"
          cy="512"
          rx="700"
          ry="280"
          transform="rotate(-24 768 512)"
        />
      </svg>
      <svg
        className="hero-ink-rays"
        viewBox="0 0 100 100"
        aria-hidden="true"
        focusable="false"
      >
        <path d="M20 35l-5-28M48 40l15-26M73 54l22-16" />
      </svg>
    </>
  );
}

export function HeroLinkExample() {
  return (
    <div className="hero-link-illustration">
      <HeroSticker className="hero-link-long" label="Before">
        <span className="hero-link-original">
          https://example.com/posts/
          <span>this-is-a-very-long-link-</span>
          <span>that-goes-on-and-on-and-on</span>
        </span>
      </HeroSticker>
      <svg
        className="hero-link-arrow"
        viewBox="0 0 24 24"
        aria-hidden="true"
        focusable="false"
      >
        <path d="M4 12H20M12 4L20 12L12 20" />
      </svg>
      <span className="hero-cut-line" aria-hidden="true">
        <Icon name="scissors" />
      </span>
      <HeroSticker className="hero-link-short" label="After" sparkle>
        smol.link/idea
      </HeroSticker>
    </div>
  );
}

function HeroSticker({
  className,
  children,
  label,
  sparkle = false,
}: {
  className: string;
  children: ReactNode;
  label: string;
  sparkle?: boolean;
}) {
  return (
    <span className={`hero-link-sticker ${className}`}>
      <span className="hero-sticker-label">{label}</span>
      <svg
        className="hero-sticker-shape"
        viewBox="0 0 320 112"
        preserveAspectRatio="none"
        aria-hidden="true"
        focusable="false"
      >
        <path
          vectorEffect="non-scaling-stroke"
          d="M16 3H304A13 13 0 0 0 317 16V24Q305 24 305 32Q305 40 317 40V48Q305 48 305 56Q305 64 317 64V72Q305 72 305 80Q305 88 317 88V96A13 13 0 0 0 304 109H16A13 13 0 0 0 3 96V88Q15 88 15 80Q15 72 3 72V64Q15 64 15 56Q15 48 3 48V40Q15 40 15 32Q15 24 3 24V16A13 13 0 0 0 16 3Z"
        />
      </svg>
      <span className="hero-sticker-text">{children}</span>
      {sparkle && (
        <svg
          className="hero-link-rays"
          viewBox="0 0 100 60"
          aria-hidden="true"
          focusable="false"
        >
          <path d="M22 44l-12-16M50 34V10M78 44l12-16" />
        </svg>
      )}
    </span>
  );
}
