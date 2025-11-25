const { merge } = require('webpack-merge');

const baseConfig = require('./webpack.base');

const config = {
  mode: 'production',
  output: {
    clean: true, // Enable clean only in production builds
  },
};

module.exports = merge(config, baseConfig);
