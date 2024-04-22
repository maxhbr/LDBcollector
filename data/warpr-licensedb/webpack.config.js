// webpack.config.js

var webpack = require("webpack");

module.exports = {
    entry: 'app',
    output: {
        path: __dirname + '/www/js',
        filename: 'app.js'
    },
    resolve: {
        root: [__dirname + '/src', __dirname],
        extensions: ['', '.jsx', '.js', '.json'],
        packageAlias: "browser"
    },
    amd: { jQuery: true },
    module: {
        preLoaders: [
            {test: /\.(js|jsx)$/, loader: "eslint-loader", include: __dirname + '/src' }
        ],
        loaders: [
            {test: /\.jsx$/, loader: "jsx-loader"}
        ]
    },
    plugins: [
        new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
    ]
};
