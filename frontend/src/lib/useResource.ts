import { useEffect, useState } from 'react';
export function useResource<T>(load: (signal: AbortSignal) => Promise<T>) {
  const [revision, setRevision] = useState(0);
  const [result, setResult] = useState<{
    owner: typeof load;
    revision: number;
    data: T | null;
    error: unknown;
  } | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    void load(controller.signal).then(
      (data) => {
        if (!controller.signal.aborted)
          setResult({ owner: load, revision, data, error: null });
      },
      (error: unknown) => {
        if (!controller.signal.aborted)
          setResult({ owner: load, revision, data: null, error });
      },
    );
    return () => controller.abort();
  }, [load, revision]);
  const current =
    result?.owner === load && result.revision === revision ? result : null;
  return {
    data: current?.data ?? null,
    error: current?.error ?? null,
    loading: current === null,
    reload: () => setRevision((r) => r + 1),
  };
}
