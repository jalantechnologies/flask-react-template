import React, { useState } from 'react';
import toast from 'react-hot-toast';

import {
  Alert,
  Button,
  Inline,
  Modal,
  Spacing,
  Stack,
  Status,
  TextField,
  Variant,
} from 'frontend/components';
import { ApiKeyService } from 'frontend/services';
import { AsyncError, CreatedApiKey } from 'frontend/types';
import { Nullable } from 'frontend/types/common-types';
import { getAccessTokenFromStorage } from 'frontend/utils/storage-util';

const apiKeyService = new ApiKeyService();

interface CreateApiKeyModalProps {
  onClose: () => void;
  onCreated: () => Promise<void>;
}

const CreateApiKeyModal: React.FC<CreateApiKeyModalProps> = ({
  onClose,
  onCreated,
}) => {
  const [name, setName] = useState<string>('');
  const [expiresInDays, setExpiresInDays] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [created, setCreated] = useState<Nullable<CreatedApiKey>>(null);

  const submit = async () => {
    const accessToken = getAccessTokenFromStorage();
    if (!accessToken) {
      return;
    }
    setIsSubmitting(true);
    try {
      const parsedExpiry = expiresInDays.trim()
        ? Number(expiresInDays)
        : undefined;
      const response = await apiKeyService.createApiKey(accessToken, {
        name: name.trim(),
        expiresInDays: parsedExpiry ?? null,
      });
      if (response.data) {
        setCreated(response.data);
        await onCreated();
      }
    } catch (error) {
      toast.error((error as AsyncError).message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const copySecret = async () => {
    if (!created) {
      return;
    }
    await navigator.clipboard.writeText(created.plaintextKey);
    toast.success('Copied to clipboard');
  };

  if (created) {
    return (
      <Modal
        title="API key created"
        width="md"
        onClose={onClose}
        testId="api-key-created-modal"
        footer={
          <Inline gap={Spacing.Sm} justify="end">
            <Button
              variant={Variant.Secondary}
              onClick={() => {
                copySecret().catch(() => undefined);
              }}
              testId="copy-api-key-button"
            >
              Copy
            </Button>
            <Button
              variant={Variant.Primary}
              onClick={onClose}
              testId="done-api-key-button"
            >
              Done
            </Button>
          </Inline>
        }
      >
        <Stack gap={Spacing.Md}>
          <Alert variant={Status.Warning}>
            Copy this key now. For security it is shown once and cannot be
            retrieved again.
          </Alert>
          <TextField
            label="Your new API key"
            value={created.plaintextKey}
            onChange={() => undefined}
            disabled
            monospace
            testId="created-api-key-value"
          />
        </Stack>
      </Modal>
    );
  }

  return (
    <Modal
      title="Create API key"
      width="md"
      onClose={onClose}
      testId="create-api-key-modal"
      footer={
        <Inline gap={Spacing.Sm} justify="end">
          <Button variant={Variant.Secondary} onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant={Variant.Primary}
            onClick={() => {
              submit().catch(() => undefined);
            }}
            isLoading={isSubmitting}
            disabled={!name.trim()}
            testId="submit-api-key-button"
          >
            Create
          </Button>
        </Inline>
      }
    >
      <Stack gap={Spacing.Md}>
        <TextField
          label="Name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="e.g. CI Deploy Bot"
          required
          autoFocus
          testId="api-key-name-input"
        />
        <TextField
          label="Expires in (days)"
          type="number"
          inputMode="numeric"
          value={expiresInDays}
          onChange={(event) => setExpiresInDays(event.target.value)}
          hint="Leave blank for a key that never expires."
          placeholder="30"
          testId="api-key-expiry-input"
        />
      </Stack>
    </Modal>
  );
};

export default CreateApiKeyModal;
