import clsx from 'clsx';
import React from 'react';
import zxcvbn, { ZXCVBNScore } from 'zxcvbn';

import Stack from 'frontend/components/layout/stack';
import Text from 'frontend/components/typography/text';
import { Emphasis, Spacing, Status } from 'frontend/types/design-system';

interface PasswordStrengthMeterProps {
  password: string;
  minScore?: number;
  testId?: string;
}

const SEGMENTS = ['first', 'second', 'third', 'fourth'] as const;

const SCORE_LABEL: Record<ZXCVBNScore, string> = {
  0: 'Very weak',
  1: 'Weak',
  2: 'Fair',
  3: 'Strong',
  4: 'Very strong',
};

const SCORE_VARIANT: Record<ZXCVBNScore, Status> = {
  0: Status.Danger,
  1: Status.Danger,
  2: Status.Warning,
  3: Status.Success,
  4: Status.Success,
};

const FILLED_SEGMENT_CLASS: Record<Status, string> = {
  [Status.Neutral]: 'bg-content-faint',
  [Status.Primary]: 'bg-primary',
  [Status.Success]: 'bg-success',
  [Status.Danger]: 'bg-danger',
  [Status.Warning]: 'bg-warning',
  [Status.Info]: 'bg-info',
  [Status.Accent]: 'bg-accent',
};

const PasswordStrengthMeter: React.FC<PasswordStrengthMeterProps> = ({
  password,
  minScore = 3,
  testId,
}) => {
  if (!password) {
    return null;
  }

  const { score, feedback } = zxcvbn(password);
  const variant = SCORE_VARIANT[score];
  const meetsMinimum = score >= minScore;
  const suggestions = feedback.suggestions ?? [];
  const summary = `Password strength: ${SCORE_LABEL[score]}`;

  return (
    <Stack gap={Spacing.Xs} testId={testId}>
      <div
        role="status"
        aria-live="polite"
        aria-label={summary}
        className="flex gap-1"
      >
        {SEGMENTS.map((segment, index) => (
          <span
            key={segment}
            aria-hidden="true"
            data-testid={testId ? `${testId}-segment-${index}` : undefined}
            className={clsx(
              'h-1 flex-1 rounded-full transition-colors',
              index < score
                ? FILLED_SEGMENT_CLASS[variant]
                : 'bg-line-strong',
            )}
          />
        ))}
      </div>
      <Text
        size="xs"
        weight="medium"
        variant={meetsMinimum ? Status.Success : variant}
        testId={testId ? `${testId}-label` : undefined}
      >
        {SCORE_LABEL[score]}
      </Text>
      {feedback.warning && (
        <Text size="xs" emphasis={Emphasis.Muted}>
          {feedback.warning}
        </Text>
      )}
      {suggestions.map((suggestion) => (
        <Text key={suggestion} size="xs" emphasis={Emphasis.Muted}>
          {suggestion}
        </Text>
      ))}
    </Stack>
  );
};

export default PasswordStrengthMeter;
