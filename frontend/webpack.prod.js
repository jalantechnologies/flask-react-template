const { merge } = require('webpack-merge');

const baseConfig = require('./webpack.base');

const config = {
  mode: 'production',
};

module.exports = merge(config, baseConfig);
