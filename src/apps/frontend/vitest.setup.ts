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
// on the native dialog throws on mount without these stand-ins. A real dialog
// reflects `open` to the attribute in both directions, so these do too.
function openDialog(this: HTMLDialogElement) {
  if (this.hasAttribute('open')) {
    return;
  }
  this.open = true;
  this.setAttribute('open', '');
}

function closeDialog(this: HTMLDialogElement, returnValue?: string) {
  if (!this.hasAttribute('open')) {
    return;
  }
  this.open = false;
  this.removeAttribute('open');
  if (returnValue !== undefined) {
    this.returnValue = returnValue;
  }
  this.dispatchEvent(new Event('close'));
}

const defineDialogMethod = (name: string, value: (...a: never[]) => void) => {
  Object.defineProperty(HTMLDialogElement.prototype, name, {
    configurable: true,
    writable: true,
    value,
  });
};

if (globalThis.HTMLDialogElement !== undefined) {
  defineDialogMethod('show', openDialog);
  defineDialogMethod('showModal', openDialog);
  defineDialogMethod('close', closeDialog);
}

afterEach(() => {
  cleanup();
  globalThis.localStorage.clear();
});
