const path = require('path')
const webpack = require('webpack')

module.exports = {
    runtimeCompiler: true,
    baseUrl: process.env.NODE_ENV === 'production'
        ? '/static/spa/'
        : '/',
    devServer: {
        proxy: {
            "/api":
                {

                    target: process.env.API || "http://localhost:8000",
                    changeOrigin: true,
                },
            "/users/api/auth": {
                target: process.env.API || "http://localhost:8000",
                changeOrigin: true,
            },
        }
    },
    configureWebpack: {
        plugins:
            process.env.NODE_ENV === 'production' ? [] : [new webpack.DefinePlugin({
                gettext: (val) => {
                    return val
                }
            })]

    },
    chainWebpack: config => {
        config.resolve.modules
            .clear()
            .add(path.resolve(__dirname, 'node_modules'))
        config.resolveLoader
            .modules
            .clear()
            .add(path.resolve(__dirname, 'node_modules'))
    }

}