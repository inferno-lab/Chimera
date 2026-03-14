import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ConnectivityProvider, useConnectivity } from './ConnectivityProvider';
import { ConnectivityStatus } from './ConnectivityStatus';

// Mock component to consume context
const Consumer = () => {
  const { isOnline, latency, isPinging } = useConnectivity();
  return (
    <div>
      <div data-testid="isOnline">{String(isOnline)}</div>
      <div data-testid="latency">{String(latency)}</div>
      <div data-testid="isPinging">{String(isPinging)}</div>
    </div>
  );
};

describe('Connectivity Feature', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    // Reset fetch mock
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: 'healthy' }),
    });
    // Clear localStorage
    localStorage.clear();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  describe('ConnectivityProvider', () => {
    it('performs initial health check on mount', async () => {
      render(
        <ConnectivityProvider>
          <Consumer />
        </ConnectivityProvider>
      );

      expect(globalThis.fetch).toHaveBeenCalledWith('/api/v1/healthz', expect.any(Object));
      
      // Wait for fetch to resolve
      await act(async () => {
        await Promise.resolve();
      });

      expect(screen.getByTestId('isOnline')).toHaveTextContent('true');
    });

    it('sets isOnline to false on fetch failure', async () => {
      globalThis.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      render(
        <ConnectivityProvider>
          <Consumer />
        </ConnectivityProvider>
      );

      await act(async () => {
        await Promise.resolve();
      });

      expect(screen.getByTestId('isOnline')).toHaveTextContent('false');
    });

    it('updates latency on successful fetch', async () => {
      // Mock performance.now to return specific values
      const nowSpy = vi.spyOn(performance, 'now');
      nowSpy.mockReturnValueOnce(1000).mockReturnValueOnce(1050); // 50ms latency

      render(
        <ConnectivityProvider>
          <Consumer />
        </ConnectivityProvider>
      );

      await act(async () => {
        await Promise.resolve();
      });

      expect(screen.getByTestId('latency')).toHaveTextContent('50');
    });

    it('polls at specified interval when autoPing is true', async () => {
      render(
        <ConnectivityProvider>
          <Consumer />
        </ConnectivityProvider>
      );

      // Initial check on mount
      expect(globalThis.fetch).toHaveBeenCalledTimes(1);

      // Advance time by 30s (default)
      await act(async () => {
        vi.advanceTimersByTime(30000);
      });

      expect(globalThis.fetch).toHaveBeenCalledTimes(2);
    });

    it('persists and loads settings from localStorage', async () => {
      localStorage.setItem('chimera-auto-ping', 'false');
      localStorage.setItem('chimera-ping-interval', '60000');

      const TestSettings = () => {
        const { autoPing, pingInterval } = useConnectivity();
        return (
          <div>
            <div data-testid="autoPing">{String(autoPing)}</div>
            <div data-testid="pingInterval">{String(pingInterval)}</div>
          </div>
        );
      };

      render(
        <ConnectivityProvider>
          <TestSettings />
        </ConnectivityProvider>
      );

      await act(async () => {
        await Promise.resolve();
      });

      expect(screen.getByTestId('autoPing')).toHaveTextContent('false');
      expect(screen.getByTestId('pingInterval')).toHaveTextContent('60000');
    });

    it('handles corrupted localStorage gracefully', async () => {
      localStorage.setItem('chimera-ping-interval', 'not-a-number');
      
      render(
        <ConnectivityProvider>
          <Consumer />
        </ConnectivityProvider>
      );

      await act(async () => {
        await Promise.resolve();
      });

      // Should still render and use default (30000)
      expect(screen.getByTestId('isOnline')).toBeInTheDocument();
    });
  });

  describe('ConnectivityStatus', () => {
    it('renders Online status correctly', async () => {
      render(
        <ConnectivityProvider>
          <ConnectivityStatus />
        </ConnectivityProvider>
      );

      await act(async () => {
        await Promise.resolve();
      });

      expect(screen.getByText('API Online')).toBeInTheDocument();
    });

    it('opens settings popover on click', async () => {
      render(
        <ConnectivityProvider>
          <ConnectivityStatus />
        </ConnectivityProvider>
      );

      await act(async () => {
        await Promise.resolve();
      });

      const button = screen.getByRole('button', { name: /Backend Connectivity Status/i });
      fireEvent.click(button);

      expect(screen.getByRole('dialog', { name: /API Connection Settings/i })).toBeInTheDocument();
      expect(button).toHaveAttribute('aria-expanded', 'true');
    });

    it('toggles autoPing settings', async () => {
      render(
        <ConnectivityProvider>
          <ConnectivityStatus />
        </ConnectivityProvider>
      );

      await act(async () => {
        await Promise.resolve();
      });

      fireEvent.click(screen.getByRole('button', { name: /Backend Connectivity Status/i }));
      
      const toggle = screen.getByRole('switch', { name: /Auto-refresh Status/i });
      expect(toggle).toHaveAttribute('aria-checked', 'true');

      fireEvent.click(toggle);
      expect(toggle).toHaveAttribute('aria-checked', 'false');
      expect(localStorage.getItem('chimera-auto-ping')).toBe('false');
    });

    it('changes ping interval', async () => {
      render(
        <ConnectivityProvider>
          <ConnectivityStatus />
        </ConnectivityProvider>
      );

      await act(async () => {
        await Promise.resolve();
      });

      fireEvent.click(screen.getByRole('button', { name: /Backend Connectivity Status/i }));
      
      const intervalBtn = screen.getByRole('button', { name: '1m' });
      fireEvent.click(intervalBtn);

      expect(intervalBtn).toHaveAttribute('aria-pressed', 'true');
      expect(localStorage.getItem('chimera-ping-interval')).toBe('60000');
    });

    it('triggers manual connectivity check', async () => {
      render(
        <ConnectivityProvider>
          <ConnectivityStatus />
        </ConnectivityProvider>
      );

      // Wait for initial mount check to finish
      await act(async () => {
        await Promise.resolve();
      });

      fireEvent.click(screen.getByRole('button', { name: /Backend Connectivity Status/i }));
      
      // Clear initial mount call
      vi.clearAllMocks();

      const checkBtn = screen.getByRole('button', { name: /Check Connectivity Now/i });
      fireEvent.click(checkBtn);

      // Await the fetch response
      await act(async () => {
        await Promise.resolve();
      });

      expect(globalThis.fetch).toHaveBeenCalledWith('/api/v1/healthz', expect.any(Object));
    });

    it('closes on Escape key', async () => {
      render(
        <ConnectivityProvider>
          <ConnectivityStatus />
        </ConnectivityProvider>
      );

      await act(async () => {
        await Promise.resolve();
      });

      fireEvent.click(screen.getByRole('button', { name: /Backend Connectivity Status/i }));
      expect(screen.queryByRole('dialog')).toBeInTheDocument();

      fireEvent.keyDown(document, { key: 'Escape' });
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });
});
