var path = require('path');
var webpack = require('webpack');
// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const CleanWebpackPlugin = require('clean-webpack-plugin');

module.exports = {
  context: __dirname,
  entry: './assets/js/index.js',
  output: {
    path: path.resolve('./assets/bundles/'),
    filename: "[name]-[hash].js",
    publicPath: '/static/bundles/'
  },
  module: {
    rules: [
      { test: /\.css$/, loader: "style-loader!css-loader" },
      {
        test: /.(ttf|otf|eot|svg|woff(2)?)(\?[a-z0-9]+)?$/,
        use: [{
          loader: 'file-loader',
          options: {
            name: '[name].[ext]',
            outputPath: './'
          }
        }]
      },
      {
        test: /\.png$/,
        loader: "url-loader?limit=100000"
      },
      {
        test: /\.jpg$/,
        loader: "file-loader"
      },
      {
      test: require.resolve('jquery'),
      use: [{
        loader: 'expose-loader',
        options: 'jQuery'
      },{
        loader: 'expose-loader',
        options: '$'
      }, {
        loader: 'expose-loader',
        options: 'moment'
      }]
    }]
  },
  plugins: [
    new webpack.ContextReplacementPlugin(/moment[\/\\]locale$/, /de|en/),
    // new BundleAnalyzerPlugin({
    //   analyzerMode: "server",
    //   analyzerHost: "127.0.0.1",
    //   analyzerPort: "8888"
    // })
  ],
  resolve: {
    alias: {
      // Force all modules to use the same jquery version.
      'jquery': path.join(__dirname, 'node_modules/jquery/src/jquery'),
      'moment': 'moment/moment.js',
      'datetimepicker': 'eonasdan-bootstrap-datetimepicker/src/js/bootstrap-datetimepicker.js'
    }
  }
}
