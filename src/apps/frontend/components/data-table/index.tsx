import clsx from 'clsx';
import React from 'react';

export interface DataTableColumn<T> {
  // Stable identity for the column, used as the React key for its header and
  // cells. A short field name (e.g. 'email', 'role') reads well.
  key: string;
  // Header label for the column.
  header: React.ReactNode;
  // Cell renderer for a row.
  cell: (row: T) => React.ReactNode;
  align?: 'left' | 'right' | 'center';
  // When true the cell text never wraps (timestamps, durations).
  nowrap?: boolean;
}

export interface DataTableProps<T> {
  columns: DataTableColumn<T>[];
  rows: T[];
  rowKey: (row: T) => string;
  testId?: string;
}

const ALIGN_CLASS: Record<
  NonNullable<DataTableColumn<unknown>['align']>,
  string
> = {
  left: 'text-left',
  right: 'text-right',
  center: 'text-center',
};

/**
 * A data table driven by typed column definitions. Header/cell styling lives
 * here once, so pages stop re-declaring TH_CLASS / TD_CLASS string constants.
 * Render this for the desktop breakpoint; pair with a card list for mobile.
 */
function DataTable<T>({
  columns,
  rowKey,
  rows,
  testId,
}: Readonly<DataTableProps<T>>): React.ReactElement {
  return (
    <table data-testid={testId} className="w-full text-left text-sm">
      <thead className="border-b border-line-subtle bg-surface-subtle">
        <tr>
          {columns.map((column) => (
            <th
              key={column.key}
              scope="col"
              className={clsx(
                'px-6 py-3 text-xs font-medium text-content-subtle',
                ALIGN_CLASS[column.align ?? 'left'],
              )}
            >
              {column.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody className="divide-y divide-line-subtle">
        {rows.map((row) => (
          <tr key={rowKey(row)} className="hover:bg-surface-subtle">
            {columns.map((column) => (
              <td
                key={column.key}
                className={clsx(
                  'px-6 py-3',
                  ALIGN_CLASS[column.align ?? 'left'],
                  column.nowrap && 'whitespace-nowrap',
                )}
              >
                {column.cell(row)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default DataTable;
