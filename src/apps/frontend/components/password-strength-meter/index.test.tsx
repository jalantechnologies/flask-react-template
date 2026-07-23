import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';

import PasswordStrengthMeter from 'frontend/components/password-strength-meter';

const filledSegments = () =>
  [0, 1, 2, 3]
    .map((index) => screen.getByTestId(`meter-segment-${index}`))
    .filter((segment) => segment.getAttribute('data-filled') === 'true').length;

describe('PasswordStrengthMeter', () => {
  it('renders nothing until a password is typed', () => {
    const { container } = render(
      <PasswordStrengthMeter testId="meter" password="" />,
    );

    expect(container).toBeEmptyDOMElement();
  });

  it('reports a weak password with few filled segments and guidance', () => {
    render(<PasswordStrengthMeter testId="meter" password="password" />);

    expect(screen.getByTestId('meter-label')).toHaveTextContent('Very weak');
    expect(filledSegments()).toBe(0);
    expect(screen.getByRole('status')).toHaveAttribute(
      'aria-label',
      'Password strength: Very weak',
    );
  });

  it('reports a strong password with the bar filled', () => {
    render(
      <PasswordStrengthMeter
        testId="meter"
        password="correct horse battery staple 12"
      />,
    );

    expect(screen.getByTestId('meter-label')).toHaveTextContent('Very strong');
    expect(filledSegments()).toBe(4);
  });

  it('strengthens the meter as the password improves', () => {
    const { rerender } = render(
      <PasswordStrengthMeter testId="meter" password="abc" />,
    );
    const weakFilled = filledSegments();

    rerender(
      <PasswordStrengthMeter
        testId="meter"
        password="a much longer unpredictable phrase 7"
      />,
    );

    expect(filledSegments()).toBeGreaterThan(weakFilled);
  });
});
