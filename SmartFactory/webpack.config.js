const path = require('path');
const webpack = require('webpack');
const TerserPlugin = require('terser-webpack-plugin');

module.exports = {
    entry: './src/index.js',
    mode: 'development',
    output: {
        path: path.resolve(__dirname, 'static/src/js/'),
        filename: 'bundle.js',
    },
    externals: [
        function ({context, request}, callback) {
            if (/^@web\/.*$/i.test(request)) {
                return callback(null, request);
            }
            callback();
        },
    ],
    experiments: {
        outputModule: true,
    },
    externalsType: 'module',
    plugins: [
        // TODO banner DOES NOT WORK in production mode, need a fix
        new webpack.BannerPlugin({
            banner: '/** @odoo-module **/',
            raw: true,
            entryOnly: false,
        }),
    ],

};