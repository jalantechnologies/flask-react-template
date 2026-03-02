const { merge } = require('webpack-merge');

const baseConfig = require('./webpack.base');

const devServerOpen = process.env.WEBPACK_DEV_DISABLE_OPEN !== 'true';
const devServerPort = process.env.PORT || 3000;
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
    historyApiFallback: true,
    hot: true,
    open: devServerOpen,
    port: devServerPort,
    proxy: {
      secure: false,
      '/api': `http://127.0.0.1:${devServerAPIProxyPort}`,
      '/assets': `http://127.0.0.1:${devServerAPIProxyPort}`,
    },
  },
};

module.exports = merge(config, baseConfig);
