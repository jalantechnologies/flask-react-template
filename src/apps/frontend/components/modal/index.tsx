import clsx from 'clsx';
import React, { PropsWithChildren, useEffect, useId, useRef } from 'react';

import IconButton from 'frontend/components/icon-button';
import CloseIcon from 'frontend/components/icons/close-icon';
import Inline from 'frontend/components/layout/inline';
import Stack from 'frontend/components/layout/stack';
import Heading from 'frontend/components/typography/heading';
import { Spacing } from 'frontend/types/design-system';

type ModalWidth = 'sm' | 'md' | 'lg';

interface ModalBaseProps {
  onClose: () => void;
  width?: ModalWidth;
  footer?: React.ReactNode;
  // Close when the backdrop (outside the panel) is clicked. Default true.
  closeOnBackdrop?: boolean;
  // Cap the panel height and let the body scroll, for long content.
  scrollable?: boolean;
  // Hide the header close button. Use when the dialog provides its own
  // dismissal (e.g. ConfirmDialog's Cancel) and backdrop-close is disabled.
  hideClose?: boolean;
  testId?: string;
}

// Every dialog needs an accessible name (WCAG 4.1.2). The type enforces it:
// pass a visible `title`, or an `ariaLabel` when the dialog has no heading
// (e.g. ConfirmDialog). One or the other is required.
type ModalProps = ModalBaseProps &
  (
    | { ariaLabel?: string; title: string }
    | { ariaLabel: string; title?: never }
  );

const WIDTH_CLASS: Record<ModalWidth, string> = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-2xl',
};

/**
 * A centered overlay dialog built on the native `<dialog>` element, which
 * provides modal semantics, the top layer, focus trapping, and Escape handling
 * for free. Owns the backdrop, panel, header, and close affordance so no page
 * hand-rolls `fixed inset-0` overlays.
 */
const Modal: React.FC<PropsWithChildren<ModalProps>> = ({
  ariaLabel,
  children,
  closeOnBackdrop = true,
  footer,
  hideClose = false,
  onClose,
  scrollable = false,
  testId,
  title,
  width = 'md',
}) => {
  const titleId = useId();
  const dialogRef = useRef<HTMLDialogElement>(null);
  // Keep the latest callbacks reachable from the mount-only listener effect
  // without re-binding (and without a stale closure).
  const handlers = useRef({ closeOnBackdrop, onClose });
  handlers.current = { closeOnBackdrop, onClose };

  // Open as a true modal (top layer + focus trap + inert background) and wire
  // native dismissal. Escape fires `cancel`; a click landing on the dialog
  // element itself (not the inner panel) is a click on the ::backdrop. These
  // listeners live on the element rather than as JSX props so the dialog stays
  // a native, non-interactive container.
  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) {
      return undefined;
    }
    dialog.showModal();

    const onCancel = (e: Event) => {
      e.preventDefault();
      handlers.current.onClose();
    };
    const onBackdrop = (e: MouseEvent) => {
      if (handlers.current.closeOnBackdrop && e.target === dialog) {
        handlers.current.onClose();
      }
    };
    dialog.addEventListener('cancel', onCancel);
    dialog.addEventListener('click', onBackdrop);

    return () => {
      dialog.removeEventListener('cancel', onCancel);
      dialog.removeEventListener('click', onBackdrop);
      dialog.close();
    };
  }, []);

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby={title ? titleId : undefined}
      aria-label={title ? undefined : ariaLabel}
      data-testid={testId}
      className={clsx(
        'w-full bg-transparent backdrop:bg-black/40',
        WIDTH_CLASS[width],
      )}
    >
      <div
        className={clsx(
          'flex w-full flex-col rounded-lg bg-surface shadow-xl',
          scrollable && 'max-h-[85vh]',
        )}
      >
        {/* Render a header when there is a title to show or a close button to
            offer. The close button is shown unless `hideClose` is set, so a
            titleless dialog still gets a dismiss affordance instead of having
            it silently dropped by the absence of a title. */}
        {(title || !hideClose) && (
          <div className="px-6 pt-5">
            <Inline justify={title ? 'between' : 'end'} align="start">
              {title && (
                <Heading level={2} id={titleId}>
                  {title}
                </Heading>
              )}
              {!hideClose && (
                <IconButton
                  label="Close"
                  icon={<CloseIcon />}
                  onClick={onClose}
                />
              )}
            </Inline>
          </div>
        )}
        <div
          className={clsx(
            'px-6 py-5',
            scrollable && 'min-h-0 flex-1 overflow-y-auto',
          )}
        >
          <Stack gap={Spacing.Md}>{children}</Stack>
        </div>
        {footer && (
          <div className="border-t border-line-subtle px-6 py-4">{footer}</div>
        )}
      </div>
    </dialog>
  );
};

export default Modal;
