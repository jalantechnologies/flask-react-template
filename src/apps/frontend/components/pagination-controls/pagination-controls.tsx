import * as React from 'react';

import Button from 'frontend/components/button';
import Inline from 'frontend/components/layout/inline';
import Text, { Emphasis } from 'frontend/components/typography/text';
import { Size, Spacing, Variant } from 'frontend/types/design-system';

interface PaginationControlsProps {
  page: number;
  pageSize: number;
  totalCount: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  testId?: string;
}

/** A bordered footer with a range count and prev/next controls. */
const PaginationControls: React.FC<PaginationControlsProps> = ({
  onPageChange,
  page,
  pageSize,
  testId,
  totalCount,
  totalPages,
}) => {
  if (totalPages <= 1) {
    return null;
  }

  return (
    <nav
      aria-label="Pagination"
      data-testid={testId}
      className="shrink-0 border-t border-line-subtle px-6 py-3"
    >
      <Inline justify="between" align="center">
        <Text size="xs" emphasis={Emphasis.Muted}>
          {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, totalCount)} of{' '}
          {totalCount}
        </Text>
        <Inline gap={Spacing.Xs}>
          <Button
            variant={Variant.Secondary}
            size={Size.Sm}
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
          >
            Previous
          </Button>
          <Button
            variant={Variant.Secondary}
            size={Size.Sm}
            disabled={page >= totalPages}
            onClick={() => onPageChange(page + 1)}
          >
            Next
          </Button>
        </Inline>
      </Inline>
    </nav>
  );
};

export default PaginationControls;
