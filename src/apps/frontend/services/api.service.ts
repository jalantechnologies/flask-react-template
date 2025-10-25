import { AxiosInstance } from 'axios';

import AppService from 'frontend/services/app.service';

export default class APIService extends AppService {
  apiClient: AxiosInstance;
  apiUrl: string;
  accountID: string;

  constructor() {
    super();
    this.apiUrl = `${this.appHost}/api`;
    this.apiClient = APIService.getAxiosInstance({
      baseURL: this.apiUrl,
    });
    const token = sessionStorage.getItem('access-token');
    this.accountID = token
      ? (JSON.parse(token) as { accountId: string })?.accountId
      : '';
  }
}
