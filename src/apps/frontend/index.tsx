import 'frontend/satoshi.css';
import 'frontend/style.css';
import React from 'react';
import ReactDOM from 'react-dom/client';

import App from 'frontend/app.component';

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('app') as HTMLElement;

  const root = ReactDOM.createRoot(container);

  root.render(<App />);
});
