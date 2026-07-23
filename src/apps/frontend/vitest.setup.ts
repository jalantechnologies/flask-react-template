import '@testing-library/jest-dom/vitest';

const noop = () => {};

try {
  Object.defineProperty(globalThis.location, 'assign', {
    configurable: true,
    value: noop,
  });
  Object.defineProperty(globalThis.location, 'replace', {
    configurable: true,
    value: noop,
  });
  Object.defineProperty(globalThis.location, 'reload', {
    configurable: true,
    value: noop,
  });
} catch {
  const url = new URL(globalThis.location.href);
  Object.defineProperty(globalThis, 'location', {
    configurable: true,
    value: Object.assign(url, {
      assign: noop,
      replace: noop,
      reload: noop,
    }),
  });
}
