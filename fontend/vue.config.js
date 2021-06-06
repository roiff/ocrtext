module.exports = {
  // publicPath :'/vue/'
  outputDir: '../backend/dist/ocrtext_fontend',
  // productionSourceMap: true,
  configureWebpack: {
    devtool: 'source-map'
  },
  devServer: {
    proxy:{
      '/api':{
        target: 'http://localhost:8099',
        changeOrigin:true,
      }
    }

  },

}
