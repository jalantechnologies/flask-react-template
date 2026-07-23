import '@testing-library/jest-dom/vitest';

const noop = () => {};

// jsdom does not implement the native <dialog> modal methods, so any component
// built on <dialog> (Modal, ConfirmDialog) throws on mount under test. Provide
// minimal implementations that flip the `open` attribute the way a real dialog
// does, enough for component and page tests to render and dismiss dialogs.
if (typeof HTMLDialogElement !== 'undefined') {
  if (!HTMLDialogElement.prototype.showModal) {
    HTMLDialogElement.prototype.showModal = function showModal(
      this: HTMLDialogElement,
    ): void {
      this.setAttribute('open', '');
    };
  }
  if (!HTMLDialogElement.prototype.close) {
    HTMLDialogElement.prototype.close = function close(
      this: HTMLDialogElement,
    ): void {
      this.removeAttribute('open');
    };
  }
}

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
