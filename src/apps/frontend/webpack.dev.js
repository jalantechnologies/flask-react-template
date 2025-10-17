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
    poll: 500,
    aggregateTimeout: 200,
    ignored: /node_modules/,
  },
  optimization: {
    runtimeChunk: 'single',
  },
  devtool: 'inline-source-map',
  devServer: {
    historyApiFallback: true,
    hot: true,
    liveReload: true,
    open: devServerOpen,
    port: devServerPort,
    host: '0.0.0.0',
    allowedHosts: 'all',
    watchFiles: {
      paths: ['src/**/*.{js,jsx,ts,tsx,css,scss}'],
      options: {
        usePolling: true,
        interval: 300,
        ignored: /node_modules/,
      },
    },
    client: {
      webSocketURL: 'auto://0.0.0.0:0/ws',
      overlay: {
        errors: true,
        warnings: false,
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
