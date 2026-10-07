export interface RuntimeConfig {
  source: 'fixture' | 'live';
  apiBase: string;
}

export function readConfig(
  env: Record<string, string | undefined>,
  production: boolean,
): RuntimeConfig {
  const source = env.VITE_DATA_SOURCE || 'live';
  if (source !== 'fixture' && source !== 'live')
    throw new Error('Invalid data source configuration.');
  if (production && source === 'fixture')
    throw new Error('Fixture data is prohibited in production builds.');
  const apiBase = (env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '');
  if (apiBase !== '/api/v1') {
    let url: URL;
    try {
      url = new URL(apiBase);
    } catch {
      throw new Error('Invalid API base URL.');
    }
    const local =
      !production && ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname);
    if (
      (url.protocol !== 'https:' && !(local && url.protocol === 'http:')) ||
      url.username ||
      url.password ||
      url.search ||
      url.hash ||
      url.pathname !== '/api/v1'
    ) {
      throw new Error(
        'API base must be /api/v1 or a secure API URL without credentials.',
      );
    }
  }
  return { source, apiBase };
}
