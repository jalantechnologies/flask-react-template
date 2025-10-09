const path = require('path');

const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const webpack = require('webpack');

// Load config with fallback for compatibility issues
let webpackBuildConfig = JSON.stringify({
  authenticationMechanism: 'EMAIL',
  datadog: {
    enabled: 'false',
  },
});

try {
  const config = require('config');
  if (config.has('public')) {
    webpackBuildConfig = JSON.stringify(config.get('public'));
  }
} catch (error) {
  console.warn('Config package error, using fallback config:', error.message);
}

module.exports = {
  target: 'web',
  entry: {
    index: path.resolve(__dirname, 'index.tsx'),
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: path.resolve(__dirname, 'index.html'),
    }),
    new MiniCssExtractPlugin({
      filename: 'style.css',
      chunkFilename: 'style.css',
    }),
    new webpack.DefinePlugin({
      'window.Config': webpackBuildConfig,
    }),
  ],
  output: {
    publicPath: '/',
    filename: '[name].bundle.js',
    clean: true,
  },
  module: {
    rules: [
      {
        test: /\.s[ac]ss$/i,
        use: [
          // Creates `style` nodes from JS strings
          'style-loader',
          // Translates CSS into CommonJS
          'css-loader',
        ],
      },
      {
        test: /\.ts(x)?$/,
        loader: 'ts-loader',
        exclude: /node_modules/,
      },
      {
        test: /\.css$/i,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          {
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: [
                  require('autoprefixer')({
                    overrideBrowserslist: ['last 2 versions'],
                  }),
                ],
              },
            },
          },
        ],
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
    alias: {
      frontend: path.resolve(__dirname),
    },
  },
};
