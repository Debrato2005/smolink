import type { ProductGateway } from './contracts';
import { adaptCreatedLink } from './adapters';
import { ApiError } from './errors';
import { request } from './client';

export function liveLinks(apiBase: string): ProductGateway {
  async function unavailable(): Promise<never> {
    throw new ApiError(
      'unavailable',
      'This feature is not connected yet. Guest link creation is available.',
    );
  }
  return {
    source: 'live',
    account: unavailable,
    list: unavailable,
    get: unavailable,
    update: unavailable,
    remove: unavailable,
    analytics: unavailable,
    qr: unavailable,
    async create(input, signal) {
      const body = await request(`${apiBase}/urls`, {
        method: 'POST',
        signal,
        body: {
          destination: input.destination,
          ...(input.alias !== undefined ? { alias: input.alias } : {}),
          ...(input.expiresAt !== undefined
            ? { expires_at: input.expiresAt }
            : {}),
        },
      });
      return adaptCreatedLink(body);
    },
  };
}
