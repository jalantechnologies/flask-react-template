import zxcvbn from 'zxcvbn';

import { Config } from 'frontend/helpers';

const DEFAULT_MIN_SCORE = 3;

export const getPasswordMinScore = (): number => {
  const configured = Config.getConfigValue<number>('password.min_zxcvbn_score');
  return typeof configured === 'number' ? configured : DEFAULT_MIN_SCORE;
};

export const isPasswordStrongEnough = (password: string): boolean => {
  if (!password) {
    return false;
  }
  return zxcvbn(password).score >= getPasswordMinScore();
};
