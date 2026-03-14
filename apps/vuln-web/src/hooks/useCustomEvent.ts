import { useEffect, useRef } from 'react';

/**
 * A generic hook to listen for custom window events safely.
 * Handles cleanup on unmount to prevent memory leaks.
 */
export function useCustomEvent<T>(eventName: string, handler: (detail: T) => void) {
  const handlerRef = useRef(handler);
  handlerRef.current = handler;

  useEffect(() => {
    const handleEvent = (event: Event) => {
      const customEvent = event as CustomEvent<T>;
      handlerRef.current(customEvent.detail);
    };

    window.addEventListener(eventName, handleEvent);
    return () => {
      window.removeEventListener(eventName, handleEvent);
    };
  }, [eventName]);
}
