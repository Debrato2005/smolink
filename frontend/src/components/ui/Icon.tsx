const paths = {
  arrow: 'M4 12h16M13 5l7 7-7 7',
  link: 'M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-2 2M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l2-2',
  copy: 'M9 9h12v12H9zM15 9V3H3v12h6',
  qr: 'M3 3h6v6H3zM15 3h6v6h-6zM3 15h6v6H3zM15 15h2v2h-2zM19 19h2v2h-2zM21 13v3M13 21v-3',
  plus: 'M12 4v16M4 12h16',
  search: 'M21 21l-5-5M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0',
  chart: 'M4 3v17h17M8 15V9M13 15V5M18 15v-4',
  check: 'M4 12l5 5L20 6',
  close: 'M5 5l14 14M5 19L19 5',
  mail: 'M3 5h18v14H3zM3 5l9 8 9-8',
  clock: 'M12 7v5l3 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0',
  trash: 'M3 6h18M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7M14 10v7',
  external: 'M14 3h7v7M21 3L10 14M10 3H3v18h18v-7',
  menu: 'M3 6h18M3 12h18M3 18h18',
  back: 'M20 12H4M11 5l-7 7 7 7',
  logout: 'M9 4H3v16h6M8 12h13M16 7l5 5-5 5',
  info: 'M12 11v6M12 7v1M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0',
} as const;
export function Icon({
  name,
  size = 20,
}: {
  name: keyof typeof paths;
  size?: number;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="square"
      strokeLinejoin="miter"
      aria-hidden="true"
    >
      <path d={paths[name]} />
    </svg>
  );
}
