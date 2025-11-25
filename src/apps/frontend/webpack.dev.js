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
  optimization: {
    runtimeChunk: 'single',
  },
  devtool: 'inline-source-map',
  devServer: {
    host: '0.0.0.0',
    port: devServerPort,
    allowedHosts: 'all',
    historyApiFallback: true,
    hot: true,
    open: devServerOpen,
    client: {
      webSocketURL: {
        hostname: '0.0.0.0',
        pathname: '/ws',
        protocol: 'ws',
      },
    },
    proxy: {
      secure: false,
      '/api': {
        target: `http://localhost:${devServerAPIProxyPort}`,
        changeOrigin: true,
      },
      '/assets': {
        target: `http://localhost:${devServerAPIProxyPort}`,
        changeOrigin: true,
      },
    },
  },
};

module.exports = merge(config, baseConfig);
