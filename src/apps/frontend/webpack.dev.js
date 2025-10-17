const { merge } = require('webpack-merge');

const baseConfig = require('./webpack.base');

const devServerOpen = process.env.WEBPACK_DEV_DISABLE_OPEN !== 'true';
const devServerPort = 3000;
const devServerAPIProxyPort = 8080;

const config = {
  mode: 'development',
  output: {
    pathinfo: true,
  },
  watchOptions: {
    poll: 500, // Check for file changes every 500ms - needed because Windows Docker doesn't propagate file system events
    aggregateTimeout: 200, // Wait 200ms after change before rebuilding - prevents multiple rebuilds for rapid file saves
    ignored: /node_modules/, // Don't watch node_modules - improves performance and prevents unnecessary rebuilds
  },
  optimization: {
    runtimeChunk: 'single',
  },
  devtool: 'inline-source-map',
  devServer: {
    historyApiFallback: true,
    hot: true, // Enable Hot Module Replacement - updates React components without full page reload
    liveReload: true, // Fallback to full page reload if HMR fails - ensures changes are always visible
    open: devServerOpen,
    port: devServerPort,
    host: '0.0.0.0', // Listen on all interfaces - allows Docker container to accept connections from host
    allowedHosts: 'all', // Accept connections from any host - required for Docker networking
    watchFiles: {
      paths: ['src/**/*.{js,jsx,ts,tsx,css,scss}'], // Watch specific file types only - improves performance by ignoring irrelevant files
      options: {
        usePolling: true, // Use polling instead of file system events - essential for Windows Docker compatibility
        interval: 300, // Check every 300ms - faster than main webpack polling for immediate feedback
        ignored: /node_modules/, // Skip node_modules - prevents watching thousands of dependency files
      },
    },
    client: {
      webSocketURL: 'auto://0.0.0.0:0/ws', // Auto-configure WebSocket URL for Docker - enables browser-server communication for hot reload
      overlay: {
        errors: true, // Show compilation errors in browser overlay - immediate feedback for syntax errors
        warnings: false, // Hide warnings in overlay - prevents clutter while developing
      },
    },
    proxy: {
      secure: false,
      '/api': `http://localhost:${devServerAPIProxyPort}`,
      '/assets': `http://localhost:${devServerAPIProxyPort}`,
    },
  },
};

module.exports = merge(config, baseConfig);
