import { act, renderHook } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import useDebouncedValue from 'frontend/utils/use-debounced-value.hook';

describe('useDebouncedValue', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('returns the initial value straight away', () => {
    const { result } = renderHook(() => useDebouncedValue('first'));

    expect(result.current).toBe('first');
  });

  it('holds the previous value until the delay has elapsed', () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebouncedValue(value, 350),
      { initialProps: { value: 'first' } },
    );

    rerender({ value: 'second' });
    expect(result.current).toBe('first');

    act(() => {
      vi.advanceTimersByTime(349);
    });
    expect(result.current).toBe('first');

    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(result.current).toBe('second');
  });

  it('defaults to a 350ms delay', () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebouncedValue(value),
      { initialProps: { value: 'first' } },
    );

    rerender({ value: 'second' });

    act(() => {
      vi.advanceTimersByTime(349);
    });
    expect(result.current).toBe('first');

    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(result.current).toBe('second');
  });

  it('restarts the delay when the value changes again mid-flight', () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebouncedValue(value, 350),
      { initialProps: { value: 'first' } },
    );

    rerender({ value: 'second' });

    act(() => {
      vi.advanceTimersByTime(300);
    });

    rerender({ value: 'third' });

    act(() => {
      vi.advanceTimersByTime(300);
    });
    expect(result.current).toBe('first');

    act(() => {
      vi.advanceTimersByTime(50);
    });
    expect(result.current).toBe('third');
  });

  it('clears its pending timer on unmount', () => {
    const clearTimeoutSpy = vi.spyOn(globalThis, 'clearTimeout');

    const { rerender, unmount } = renderHook(
      ({ value }) => useDebouncedValue(value, 350),
      { initialProps: { value: 'first' } },
    );

    rerender({ value: 'second' });
    unmount();

    expect(clearTimeoutSpy).toHaveBeenCalled();

    act(() => {
      vi.advanceTimersByTime(1_000);
    });

    expect(vi.getTimerCount()).toBe(0);
  });

  it('works with non-string values', () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebouncedValue(value, 100),
      { initialProps: { value: { page: 1 } } },
    );

    const next = { page: 2 };
    rerender({ value: next });

    act(() => {
      vi.advanceTimersByTime(100);
    });

    expect(result.current).toBe(next);
  });
});
