import '@testing-library/jest-dom/vitest';

const { href, origin, protocol, host, hostname, port, pathname, search, hash } =
  window.location;

Object.defineProperty(window, 'location', {
  configurable: true,
  writable: true,
  value: {
    href,
    origin,
    protocol,
    host,
    hostname,
    port,
    pathname,
    search,
    hash,
    assign: () => {},
    replace: () => {},
    reload: () => {},
  },
});
