import clsx from 'clsx';
import React, { PropsWithChildren, useEffect, useId } from 'react';

import useClickOutside from 'frontend/utils/use-click-outside.hook';

type MenuAlign = 'left' | 'right' | 'stretch';
type MenuDirection = 'down' | 'up';

interface MenuProps {
  // The element that opens the menu, mirroring shadcn's DropdownMenuTrigger.
  // Must NOT be a button or other interactive element — Menu wraps it in a
  // <button>, and nesting interactive elements is invalid HTML. Pass an
  // Avatar, icon, or a layout primitive (Inline/Stack/Text) instead.
  trigger: React.ReactNode;
  align?: MenuAlign;
  direction?: MenuDirection;
  // Accessible name for the trigger button (it wraps arbitrary trigger content).
  ariaLabel?: string;
  testId?: string;
}

const ALIGN_CLASS: Record<MenuAlign, string> = {
  left: 'left-0',
  right: 'right-0',
  stretch: 'inset-x-0',
};

const DIRECTION_CLASS: Record<MenuDirection, string> = {
  down: 'top-full mt-1',
  up: 'bottom-full mb-1',
};

// Lets a MenuItem close the panel after activating, so the panel container
// does not need a click handler on a non-interactive element.
const MenuContext = React.createContext<() => void>(() => undefined);

/**
 * A dropdown panel: a trigger button plus a floating panel that closes on
 * outside click or Escape. The panel holds arbitrary content (MenuItem rows,
 * filters, headers), so it is a generic popover rather than an ARIA `menu`.
 */
const Menu: React.FC<PropsWithChildren<MenuProps>> = ({
  align = 'right',
  ariaLabel,
  children,
  direction = 'down',
  testId,
  trigger,
}) => {
  const { isOpen, ref, setIsOpen } = useClickOutside();
  const panelId = useId();
  const close = React.useCallback(() => setIsOpen(false), [setIsOpen]);

  // Close on Escape from anywhere while open, including when focus is inside a
  // MenuItem. A document listener keeps Escape working without attaching a
  // keyboard handler to the non-interactive panel container.
  useEffect(() => {
    if (!isOpen) {
      return undefined;
    }
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, setIsOpen]);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        aria-expanded={isOpen}
        aria-controls={isOpen ? panelId : undefined}
        aria-label={ariaLabel}
        data-testid={testId}
        onClick={() => setIsOpen((v) => !v)}
        className="w-full text-left"
      >
        {trigger}
      </button>
      {isOpen && (
        <MenuContext.Provider value={close}>
          <div
            id={panelId}
            className={clsx(
              'absolute z-20 min-w-44 overflow-hidden rounded-md border border-line-subtle bg-surface shadow-lg',
              ALIGN_CLASS[align],
              DIRECTION_CLASS[direction],
            )}
          >
            {children}
          </div>
        </MenuContext.Provider>
      )}
    </div>
  );
};

type MenuSectionBorder = 'top' | 'bottom' | 'none';

interface MenuSectionProps {
  // A bordered, padded region inside a menu panel for non-item content (a user
  // header, a brand footer). `border` places the rule that separates it from
  // the MenuItem rows.
  border?: MenuSectionBorder;
  testId?: string;
}

const MENU_SECTION_BORDER_CLASS: Record<MenuSectionBorder, string> = {
  top: 'border-t border-line-subtle',
  bottom: 'border-b border-line-subtle',
  none: '',
};

/**
 * A non-interactive, bordered section inside a `Menu` panel. Use it for a
 * header or footer band around the `MenuItem` rows instead of hand-writing a
 * bordered, padded `<div>` at the call-site.
 */
export const MenuSection: React.FC<PropsWithChildren<MenuSectionProps>> = ({
  border = 'none',
  children,
  testId,
}) => (
  <div
    data-testid={testId}
    className={clsx('px-3 py-2.5', MENU_SECTION_BORDER_CLASS[border])}
  >
    {children}
  </div>
);

interface MenuItemProps {
  onClick: () => void;
  testId?: string;
}

/** A single selectable row inside a `Menu`. A native button, so it is keyboard- and screen-reader-accessible. */
export const MenuItem: React.FC<PropsWithChildren<MenuItemProps>> = ({
  children,
  onClick,
  testId,
}) => {
  const close = React.useContext(MenuContext);
  return (
    <button
      type="button"
      data-testid={testId}
      onClick={() => {
        onClick();
        close();
      }}
      className="block w-full px-3 py-2 text-left text-xs text-content-subtle hover:bg-surface-subtle hover:text-content"
    >
      {children}
    </button>
  );
};

export default Menu;
