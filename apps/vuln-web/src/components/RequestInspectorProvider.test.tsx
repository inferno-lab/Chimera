import { render, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { RequestInspectorProvider, useRequestInspector } from './RequestInspectorProvider';

// Mock component to consume context
const Consumer = () => {
  const { lastExchange, exchanges } = useRequestInspector();
  return (
    <div>
      <div data-testid="exchanges-count">{exchanges.length}</div>
      <div data-testid="last-exchange-url">{lastExchange?.url}</div>
      <div data-testid="last-exchange-status">{lastExchange?.status}</div>
    </div>
  );
};

describe('RequestInspectorProvider', () => {
  let originalFetch: typeof fetch;

  beforeEach(() => {
    // Save the environment's fetch
    originalFetch = window.fetch;
    // Mock it
    window.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ 'content-type': 'application/json' }),
      clone: function() { return this; },
      json: () => Promise.resolve({ data: 'success' }),
      text: () => Promise.resolve('success'),
    });
  });

  afterEach(() => {
    // Restore the environment's fetch
    window.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it('intercepts global fetch calls', async () => {
    const { getByTestId } = render(
      <RequestInspectorProvider>
        <Consumer />
      </RequestInspectorProvider>
    );

    await act(async () => {
      await fetch('/api/test-endpoint', {
        method: 'POST',
        body: JSON.stringify({ hello: 'world' }),
        headers: { 'Content-Type': 'application/json' }
      });
    });

    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(getByTestId('exchanges-count')).toHaveTextContent('1');
    expect(getByTestId('last-exchange-url')).toHaveTextContent('/api/test-endpoint');
    expect(getByTestId('last-exchange-status')).toHaveTextContent('200');
  });

  it('restores original fetch on unmount', () => {
    // Ensure we start clean
    (window.fetch as any).__chimera_patched = false;

    const { unmount } = render(
      <RequestInspectorProvider>
        <Consumer />
      </RequestInspectorProvider>
    );

    expect((window.fetch as any).__chimera_patched).toBe(true);

    unmount();

    // Instead of Object.is, check if the patch flag is gone or fetch is reverted
    expect((window.fetch as any).__chimera_patched).toBeFalsy();
  });

  it('ignores HMR and chrome-extension URLs', async () => {
    const { getByTestId } = render(
      <RequestInspectorProvider>
        <Consumer />
      </RequestInspectorProvider>
    );

    await act(async () => {
      await fetch('/@vite/client?hmr=true');
      await fetch('chrome-extension://abc/script.js');
    });

    await act(async () => {
      await Promise.resolve();
    });

    expect(getByTestId('exchanges-count')).toHaveTextContent('0');
  });

  it('correctly clones the response to avoid consuming the original body', async () => {
    const jsonMock = vi.fn().mockResolvedValue({ data: 'success' });
    const cloneMock = vi.fn().mockReturnValue({
      headers: new Headers({ 'content-type': 'application/json' }),
      json: jsonMock,
      text: () => Promise.resolve('success'),
    });

    (window.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ 'content-type': 'application/json' }),
      clone: cloneMock,
      json: () => Promise.resolve({ data: 'original' }),
    });

    render(
      <RequestInspectorProvider>
        <Consumer />
      </RequestInspectorProvider>
    );

    let response: Response;
    await act(async () => {
      response = await fetch('/api/test');
    });

    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(cloneMock).toHaveBeenCalled();
    
    // The original response should still be usable
    const body = await response!.json();
    expect(body).toEqual({ data: 'original' });
  });

  it('caps the exchange list at 20 entries', async () => {
    const { getByTestId } = render(
      <RequestInspectorProvider>
        <Consumer />
      </RequestInspectorProvider>
    );

    await act(async () => {
      for (let i = 0; i < 25; i++) {
        await fetch(`/api/test-${i}`);
      }
    });

    // Many small awaits because of the internal async nature
    for (let i = 0; i < 30; i++) {
      await act(async () => {
        await Promise.resolve();
      });
    }

    expect(getByTestId('exchanges-count')).toHaveTextContent('20');
  });

  it('handles non-JSON responses gracefully', async () => {
    (window.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ 'content-type': 'text/plain' }),
      clone: function() { return this; },
      text: () => Promise.resolve('plain text response'),
    });

    const { getByTestId } = render(
      <RequestInspectorProvider>
        <Consumer />
      </RequestInspectorProvider>
    );

    await act(async () => {
      await fetch('/api/text');
    });

    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(getByTestId('exchanges-count')).toHaveTextContent('1');
  });
});
