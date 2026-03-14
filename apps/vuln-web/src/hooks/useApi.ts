import { useState, useCallback, useRef, useEffect } from 'react';
import { API_BASE_URL } from '../lib/config';

interface UseApiOptions {
  method?: string;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

/**
 * A thin hook for making API requests to the Chimera backend.
 * Automatically handles API_BASE_URL and JSON content types.
 * 
 * Note: Security logging is handled at the fetch interceptor level
 * in RequestInspectorProvider, so this hook doesn't need to manually
 * call dispatchAttackLog.
 */
export function useApi<T = any>() {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const request = useCallback(async (
    path: string,
    body?: any,
    options: UseApiOptions = {}
  ): Promise<T | null> => {
    // Cancel previous request if any
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    abortControllerRef.current = new AbortController();
    const signal = options.signal || abortControllerRef.current.signal;

    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const url = path.startsWith('http') ? path : `${API_BASE_URL}${path}`;
      const res = await fetch(url, {
        method: options.method || (body ? 'POST' : 'GET'),
        headers: {
          ...(body ? { 'Content-Type': 'application/json' } : {}),
          ...options.headers,
        },
        ...(body ? { body: JSON.stringify(body) } : {}),
        signal,
      });

      if (!res.ok) {
        throw new Error(`API Request failed with status ${res.status}`);
      }

      const contentType = res.headers.get('content-type');
      let data: T;
      
      if (contentType && contentType.includes('application/json')) {
        data = await res.json();
      } else {
        data = await res.text() as unknown as T;
      }

      setState({ data, loading: false, error: null });
      return data;
    } catch (err: any) {
      if (err.name === 'AbortError') {
        // Request was aborted, don't update state
        return null;
      }
      const errorMessage = err.message || 'An unknown error occurred';
      setState({ data: null, loading: false, error: errorMessage });
      return null;
    } finally {
      abortControllerRef.current = null;
    }
  }, []);

  const clear = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, request, clear };
}
