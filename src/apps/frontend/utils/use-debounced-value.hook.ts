import { useEffect, useState } from 'react';

const DEFAULT_DELAY_IN_MILLISECONDS = 350;

const useDebouncedValue = <T>(
  value: T,
  delayInMilliseconds: number = DEFAULT_DELAY_IN_MILLISECONDS,
): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setDebouncedValue(value);
    }, delayInMilliseconds);

    return () => clearTimeout(timeoutId);
  }, [value, delayInMilliseconds]);

  return debouncedValue;
};

export default useDebouncedValue;
