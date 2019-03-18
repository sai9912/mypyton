const path = require('path');
const webpack = require('webpack');

var webpackConf = {
    entry: {
        productedit: './src/productedit/index.js',
        productcreate: './src/productcreate/index.js',
    },
    output: {
        path: path.resolve(__dirname, '../backend/public/js'),
        publicPath: '/js/',
        filename: 'build.js'
    },
    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: 'vue-loader',
                options: {
                    loaders: {
                        css: "css-loader",
                        stylus: "css-loader!stylus-loader"
                    }
                }
            },
            {
                test: /\.js$/,
                loader: 'babel-loader',
                exclude: /node_modules/
            },
            {
                test: /\.css/,
                loader: "css-loader"
            },
            {
                test: /\.(png|jpg|gif|svg)$/,
                loader: 'file-loader',
                options: {
                    name: '[name].[ext]?[hash]'
                }
            }
        ]
    },
    resolve: {
        modules: [
            'node_modules'
        ],
        alias: {
            'vue$': 'vue/dist/vue.esm.js',
            'jquery-ui': 'jquery-ui/ui'
        },
        extensions: ['*', '.js', '.vue', '.json']
    },
    devServer: {
        historyApiFallback: true,
        noInfo: true,
        overlay: true
    },
    performance: {
        hints: false
    },
    devtool: '#eval-source-map',
    plugins: [
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
            'window.jQuery': 'jquery',
            Popper: ['popper.js', 'default']
        })
    ]
};


module.exports = function (config) {
    config.set({
        browsers: ['Chrome'],
        frameworks: ['mocha', 'sinon-chai'],
        reporters: ['spec', 'coverage'],
        files: ['./index.js'],
        preprocessors: {
            './index.js': ['webpack', 'sourcemap'],
            ['/var/www/reis_sprl/BCM_multihosted/UI/vuejs/src/**/*.js']: ['coverage']
        },
        plugins: [
            'karma-chrome-launcher',
            //'karma-jspm', 'karma-phantomjs-launcher',

            'karma-mocha',
            'karma-sinon-chai',

            'karma-webpack',
            'karma-sourcemap-loader',

            'karma-spec-reporter',
            'karma-coverage'
        ],
        webpack: webpackConf,
        webpackMiddleware: {
            noInfo: true
        },
        coverageReporter: {
            dir: './coverage',
            reporters: [
                {type: 'html'},
                {type: 'text-summary'},
                {type: 'lcovonly', subdir: '.'},
                {type: 'json', subdir: '.'}
            ]
        },
        client: {
            chai: {
                includeStack: true
            }
        }
    })
}
