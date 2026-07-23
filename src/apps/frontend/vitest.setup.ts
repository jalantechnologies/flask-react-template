import '@testing-library/jest-dom/vitest';

const noop = () => {};

try {
  Object.defineProperty(window.location, 'assign', {
    configurable: true,
    value: noop,
  });
  Object.defineProperty(window.location, 'replace', {
    configurable: true,
    value: noop,
  });
  Object.defineProperty(window.location, 'reload', {
    configurable: true,
    value: noop,
  });
} catch {
  const url = new URL(window.location.href);
  Object.defineProperty(window, 'location', {
    configurable: true,
    value: Object.assign(url, {
      assign: noop,
      replace: noop,
      reload: noop,
    }),
  });
}
