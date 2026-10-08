export function HeroBackdrop() {
  return (
    <svg
      className="hero-backdrop"
      viewBox="0 0 1536 1024"
      aria-hidden="true"
      focusable="false"
    >
      <path
        className="hero-backdrop-fill"
        d="M110 710C270 470 940 120 1210 125C1410 125 1510 305 1410 470C1290 665 565 1015 265 960C85 928 25 840 110 710Z"
      />
      <path
        className="hero-ink-rays"
        d="M1255 85l-6-55M1320 99l28-49M1370 139l43-30"
      />
    </svg>
  );
}

export function HeroLinkExample() {
  return (
    <div className="hero-link-illustration">
      <span className="hero-link-sticker hero-link-long">
        example.com/a/very/long/link
        <span>/that/keeps/going/on/and/on/and/on</span>
      </span>
      <svg
        className="hero-link-arrow"
        viewBox="0 0 100 60"
        aria-hidden="true"
        focusable="false"
      >
        <path d="M8 38C26 10 55 12 82 36M80 18l6 21-22-3" />
      </svg>
      <span className="hero-link-sticker hero-link-short">smol.link/idea</span>
      <svg
        className="hero-link-rays"
        viewBox="0 0 100 100"
        aria-hidden="true"
        focusable="false"
      >
        <path d="M25 24l-5-15M48 24l5-16M68 33l14-10" />
      </svg>
    </div>
  );
}
