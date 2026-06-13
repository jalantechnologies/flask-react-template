import React from 'react';

import Button from 'frontend/components/button';
import Inline from 'frontend/components/layout/inline';
import Modal from 'frontend/components/modal';
import Text, { Emphasis } from 'frontend/components/typography/text';
import { Spacing, Variant } from 'frontend/types/design-system';

interface ConfirmDialogProps {
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  title?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean;
  testId?: string;
}

/**
 * A yes/no confirmation built on Modal. The single way to ask the user to
 * confirm a destructive or significant action.
 */
const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  cancelLabel = 'Cancel',
  confirmLabel = 'Confirm',
  danger = false,
  message,
  onCancel,
  onConfirm,
  testId,
  title,
}) => {
  // A visible title names the dialog; without one, a generic label names it so
  // the message isn't announced twice (once as the dialog name, once as the
  // body Text). Spreading satisfies Modal's "title or ariaLabel" type.
  const nameProps = title ? { title } : { ariaLabel: 'Confirmation' };
  return (
    <Modal
      {...nameProps}
      width="sm"
      onClose={onCancel}
      closeOnBackdrop={false}
      hideClose
      testId={testId}
      footer={
        <Inline gap={Spacing.Sm} justify="end">
          <Button variant={Variant.Secondary} onClick={onCancel}>
            {cancelLabel}
          </Button>
          <Button
            variant={danger ? Variant.Danger : Variant.Primary}
            onClick={onConfirm}
          >
            {confirmLabel}
          </Button>
        </Inline>
      }
    >
      <Text emphasis={Emphasis.Subtle}>{message}</Text>
    </Modal>
  );
};

export default ConfirmDialog;
