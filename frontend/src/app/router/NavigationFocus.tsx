import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router';

export function NavigationFocus() {
  const { pathname, hash, search } = useLocation();
  const view = new URLSearchParams(search).get('view');
  const surface = pathname + (view === 'analytics' ? '?view=analytics' : '');
  const previous = useRef(surface);
  useEffect(() => {
    const heading = document.querySelector('main h1')?.textContent;
    document.title = heading ? `${heading} · Smolink` : 'Smolink';
    if (previous.current !== surface) {
      document.getElementById('main')?.focus();
      window.scrollTo(0, 0);
    }
    if (['#how-it-works', '#questions', '#shorten'].includes(hash))
      document.querySelector(hash)?.scrollIntoView();
    previous.current = surface;
  }, [surface, hash]);
  return null;
}
