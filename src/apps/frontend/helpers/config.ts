import _ from 'lodash';

export const getConfigValue = <T = string>(key: string): T | undefined =>
  _.get(window.Config, key) as T | undefined;

export default getConfigValue;
