import type { RuntimeConfig } from '../config/runtime';
import type { ProductGateway } from './contracts';
import { liveLinks } from './live';

export async function createLinkGateway(
  config: RuntimeConfig,
): Promise<ProductGateway> {
  // Vite removes this branch and the fixture chunk from production builds.
  if (import.meta.env.DEV && config.source === 'fixture') {
    return (await import('./fixtures')).fixtureLinks;
  }
  if (config.source !== 'live')
    throw new Error('Fixture mode is unavailable in this build.');
  return liveLinks(config.apiBase);
}
