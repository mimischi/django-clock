const BundleTracker = require('webpack-bundle-tracker');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const merge = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
  devtool: 'inline-source-map',
  devServer: {
    contentBase: './assets/bundles/'
  },
  plugins: [
    new BundleTracker({filename: './webpack-stats-local.json'}),
    new CleanWebpackPlugin(['./assets/bundles/']),
  ]
});
