import { AxiosInstance } from 'axios';

import AppService from 'frontend/services/app.service';

export default class APIService extends AppService {
  apiClient: AxiosInstance;
  apiUrl: string;

  constructor() {
    super();
    this.apiUrl = `${this.appHost}/api`;
    this.apiClient = APIService.getAxiosInstance({
      baseURL: this.apiUrl,
    });
    this.apiClient.interceptors.request.use((config) => {
      const raw = localStorage.getItem('access-token');
      if (raw) {
        try {
          const parsed = JSON.parse(raw);
          if (parsed.token) {
            config.headers['Authorization'] = `Bearer ${parsed.token}`;
          }
        } catch (err) {
          console.error('Failed to parse access_token from localStorage', err);
        }
      }
      return config;
    });
  }
}
