import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { matchRoutes } from 'react-router';
import '@fontsource/space-grotesk/latin-700.css';
import '@fontsource/inter/latin-400.css';
import '@fontsource/inter/latin-600.css';
import '@fontsource/space-mono/latin-400.css';
import './styles/tokens.css';
import './styles/globals.css';
import { App } from './app/App';
import { readConfig } from './lib/config/runtime';
import { createLinkGateway } from './lib/api/gateway';

// Keep one-time email credentials in memory only. Remove the fragment before rendering.
let initialToken = '';
if (
  matchRoutes(
    [{ path: '/verify-email' }, { path: '/reset-password' }],
    window.location.pathname,
  ) &&
  window.location.hash
) {
  initialToken =
    new URLSearchParams(window.location.hash.slice(1)).get('token') ?? '';
  window.history.replaceState(
    null,
    '',
    window.location.pathname + window.location.search,
  );
}
const root = document.getElementById('root');
if (!root) throw new Error('Missing application mount point.');
try {
  const config = readConfig(import.meta.env, import.meta.env.PROD);
  const links = await createLinkGateway(config);
  createRoot(root).render(
    <StrictMode>
      <App links={links} initialToken={initialToken} />
    </StrictMode>,
  );
} catch {
  const main = document.createElement('main');
  const heading = document.createElement('h1');
  heading.textContent = 'Smolink could not start.';
  const message = document.createElement('p');
  message.setAttribute('role', 'alert');
  message.textContent =
    'Check the application configuration, then reload the page.';
  main.append(heading, message);
  root.replaceChildren(main);
}
