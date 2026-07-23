import React, { useCallback, useEffect, useState } from 'react';
import toast from 'react-hot-toast';

import {
  Badge,
  Button,
  Card,
  ConfirmDialog,
  DataTable,
  DataTableColumn,
  Emphasis,
  EmptyState,
  Heading,
  Loading,
  Page,
  PageBody,
  Size,
  Spacing,
  Stack,
  Status,
  Text,
  Toolbar,
  Variant,
} from 'frontend/components';
import CreateApiKeyModal from 'frontend/pages/api-keys/create-api-key-modal';
import { ApiKeyService } from 'frontend/services';
import { ApiKey, ApiKeyStatus, AsyncError } from 'frontend/types';
import { Nullable } from 'frontend/types/common-types';
import { getAccessTokenFromStorage } from 'frontend/utils/storage-util';

const apiKeyService = new ApiKeyService();

const STATUS_VARIANT: Record<ApiKeyStatus, Status> = {
  [ApiKeyStatus.ACTIVE]: Status.Success,
  [ApiKeyStatus.REVOKED]: Status.Danger,
  [ApiKeyStatus.EXPIRED]: Status.Warning,
};

const formatTimestamp = (value: Nullable<string>): string => {
  if (!value) {
    return 'Never';
  }
  return new Date(value).toLocaleString();
};

const ApiKeysPage: React.FC = () => {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isCreateOpen, setIsCreateOpen] = useState<boolean>(false);
  const [keyPendingRevoke, setKeyPendingRevoke] =
    useState<Nullable<ApiKey>>(null);

  const loadKeys = useCallback(async () => {
    const accessToken = getAccessTokenFromStorage();
    if (!accessToken) {
      return;
    }
    setIsLoading(true);
    try {
      const response = await apiKeyService.listApiKeys(accessToken);
      setApiKeys(response.data ?? []);
    } catch (error) {
      toast.error((error as AsyncError).message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadKeys().catch(() => undefined);
  }, [loadKeys]);

  const confirmRevoke = useCallback(async () => {
    const accessToken = getAccessTokenFromStorage();
    if (!accessToken || !keyPendingRevoke) {
      return;
    }
    try {
      await apiKeyService.revokeApiKey(accessToken, keyPendingRevoke.id);
      toast.success('API key revoked');
      await loadKeys();
    } catch (error) {
      toast.error((error as AsyncError).message);
    } finally {
      setKeyPendingRevoke(null);
    }
  }, [keyPendingRevoke, loadKeys]);

  const columns: DataTableColumn<ApiKey>[] = [
    { key: 'name', header: 'Name', cell: (row) => row.name },
    {
      key: 'status',
      header: 'Status',
      cell: (row) => (
        <Badge variant={STATUS_VARIANT[row.status]} testId={`status-${row.id}`}>
          {row.status}
        </Badge>
      ),
    },
    {
      key: 'created_at',
      header: 'Created',
      nowrap: true,
      cell: (row) => formatTimestamp(row.createdAt),
    },
    {
      key: 'expires_at',
      header: 'Expires',
      nowrap: true,
      cell: (row) => formatTimestamp(row.expiresAt),
    },
    {
      key: 'last_used_at',
      header: 'Last used',
      nowrap: true,
      cell: (row) => formatTimestamp(row.lastUsedAt),
    },
    {
      key: 'actions',
      header: '',
      align: 'right',
      cell: (row) =>
        row.status === ApiKeyStatus.ACTIVE ? (
          <Button
            variant={Variant.Danger}
            size={Size.Sm}
            onClick={() => setKeyPendingRevoke(row)}
            testId={`revoke-${row.id}`}
          >
            Revoke
          </Button>
        ) : null,
    },
  ];

  return (
    <Page testId="api-keys-page">
      <PageBody>
        <Stack gap={Spacing.Lg}>
          <Toolbar>
            <Stack gap={Spacing.Xs}>
              <Heading level={1}>API keys</Heading>
              <Text emphasis={Emphasis.Muted}>
                Create keys for services and integrations to call the API
                without an interactive login. A key is shown once at creation.
              </Text>
            </Stack>
            <Button
              variant={Variant.Primary}
              onClick={() => setIsCreateOpen(true)}
              testId="create-api-key-button"
            >
              Create API key
            </Button>
          </Toolbar>

          {isLoading && <Loading testId="api-keys-loading" />}

          {!isLoading && apiKeys.length === 0 && (
            <EmptyState
              testId="api-keys-empty"
              title="No API keys yet"
              description="Create your first key to authenticate a service or integration."
            />
          )}

          {!isLoading && apiKeys.length > 0 && (
            <Card variant="outlined">
              <DataTable
                testId="api-keys-table"
                columns={columns}
                rows={apiKeys}
                rowKey={(row) => row.id}
              />
            </Card>
          )}
        </Stack>
      </PageBody>

      {isCreateOpen && (
        <CreateApiKeyModal
          onClose={() => setIsCreateOpen(false)}
          onCreated={loadKeys}
        />
      )}

      {keyPendingRevoke && (
        <ConfirmDialog
          testId="revoke-confirm-dialog"
          title="Revoke API key"
          message={`Revoke "${keyPendingRevoke.name}"? Any service using it will stop working immediately. This cannot be undone.`}
          confirmLabel="Revoke"
          danger
          onConfirm={() => {
            void confirmRevoke();
          }}
          onCancel={() => setKeyPendingRevoke(null)}
        />
      )}
    </Page>
  );
};

export default ApiKeysPage;
