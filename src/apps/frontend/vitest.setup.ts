import '@testing-library/jest-dom/vitest';

import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

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

// jsdom parses <dialog> but implements none of its methods, so anything built
// on the native dialog throws on mount without these stand-ins.
const polyfillDialogMethods = () => {
  const open = function open(this: HTMLDialogElement) {
    this.open = true;
  };

  const close = function close(this: HTMLDialogElement, returnValue?: string) {
    if (!this.open) {
      return;
    }
    this.open = false;
    if (returnValue !== undefined) {
      this.returnValue = returnValue;
    }
    this.dispatchEvent(new Event('close'));
  };

  const define = (name: string, value: (...args: never[]) => void) => {
    Object.defineProperty(HTMLDialogElement.prototype, name, {
      configurable: true,
      writable: true,
      value,
    });
  };

  define('show', open);
  define('showModal', open);
  define('close', close);
};

if (typeof globalThis.HTMLDialogElement !== 'undefined') {
  polyfillDialogMethods();
}

afterEach(() => {
  cleanup();
  globalThis.localStorage.clear();
});
