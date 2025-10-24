import axios, { AxiosInstance, CreateAxiosDefaults } from 'axios';

export default class AppService {
  appHost: string;

  constructor() {
    this.appHost = `${window.location.protocol}//${window.location.host}`;
  }

  static getAxiosInstance(config?: CreateAxiosDefaults): AxiosInstance {
    // returns an axios instance which can be used by services
    // to make remote calls
    return axios.create(config);
  }
}
