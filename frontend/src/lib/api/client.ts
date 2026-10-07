import { ApiError, httpError } from './errors';

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  body?: unknown;
  signal?: AbortSignal | undefined;
  accessToken?: string;
  timeoutMs?: number;
}

export async function request(
  url: string,
  options: RequestOptions = {},
): Promise<unknown> {
  const method = options.method ?? 'GET';
  const mutation = method !== 'GET';
  if (options.signal?.aborted)
    throw new ApiError('cancelled', 'The request was cancelled.');
  const controller = new AbortController();
  let timedOut = false;
  const timer = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, options.timeoutMs ?? 10000);
  const cancel = () => controller.abort();
  options.signal?.addEventListener('abort', cancel, { once: true });
  try {
    const headers: Record<string, string> = { Accept: 'application/json' };
    if (options.body !== undefined)
      headers['Content-Type'] = 'application/json';
    if (options.accessToken)
      headers.Authorization = `Bearer ${options.accessToken}`;
    const response = await fetch(url, {
      method,
      headers,
      signal: controller.signal,
      credentials: 'omit',
      redirect: 'error',
      ...(options.body !== undefined
        ? { body: JSON.stringify(options.body) }
        : {}),
    });
    const raw = response.status === 204 ? '' : await response.text();
    let body: unknown = null;
    if (raw) {
      try {
        body = JSON.parse(raw) as unknown;
      } catch {
        if (response.ok)
          throw new ApiError(
            'invalid_response',
            'The service returned an invalid response.',
            response.status,
            'unknown',
            {},
            null,
            mutation,
          );
      }
    }
    if (!response.ok)
      throw httpError(
        response.status,
        body,
        response.headers.get('Retry-After'),
        mutation,
      );
    if (!raw && response.status !== 204 && response.status !== 202)
      throw new ApiError(
        'invalid_response',
        'The service returned an empty response.',
        response.status,
        'unknown',
        {},
        null,
        mutation,
      );
    return body;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    const code = timedOut
      ? 'timeout'
      : controller.signal.aborted
        ? 'cancelled'
        : 'network';
    throw new ApiError(
      code,
      code === 'timeout'
        ? 'The request timed out.'
        : code === 'cancelled'
          ? 'The request was cancelled.'
          : 'The service could not be reached.',
      0,
      'unknown',
      {},
      null,
      mutation,
    );
  } finally {
    clearTimeout(timer);
    options.signal?.removeEventListener('abort', cancel);
  }
}
