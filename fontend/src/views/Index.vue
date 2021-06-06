<template>
  <div class="wrapper">
    <a-row>
      <a-col :lg="10" :md="10" :sm="9">
        <div class="left-wrapper">
          <!-- <div class="up-img-wrapper"> -->
          <!-- :beforeUpload="beforeUpload" -->
          <div class="upimg-dragger">
            <a-upload-dragger
              name="file"
              action="/tools/ocr_text/"
              @change="handleChange"
              accept=".jpg, .jpeg, .png, .gif, .ico"
              :beforeUpload="beforeUpload"
              listType="picture"
              :showUploadList="false"
            >
              <p>点击、拖动、或者粘贴图片</p>
            </a-upload-dragger>
          </div>
          <div class="up-img-preview">
            <img :src="upImage" alt="预览图片" :hidden="previewImgHidden" />
          </div>
          <!-- </div> -->
          <div style="margin-top:1rem;">
            <p>
              重要说明:
            </p>
            <p>
              文字范围: 文字范围是一个二维数组，如: [[0,0,10,10],[20,20,50,50]]，
              该参数记录了需要检测的文本框范围，
              参数不填写时，自动检测文本框，否则按照给出的范围识别，
              条件允许的情况下，手动输入文本框范围，可以提高准确性，尤其是文本框特别小的时候，自动检测并不准确
            </p>
            <p>
             白名单: 白名单是指只返回白名单中所包含的字符串，可以防止识别成其他类似的文字，比如: "千"和"干"就很容易识别错误
            </p>
            <p>
              色偏列表: 色偏列表是一个二维数组，如 [[0x000000,0x222222],[0x333333,0x555555]]，
              支持多组偏色，用法类似大漠的取偏色表，多取几个颜色，会自动计算出颜色范围，
              一个列表内存放一组色偏值(即相近的颜色放到一个列表内)，
            </p>
            <p>
              压缩图片: 这是一个在自动识别文本框时才生效的参数，默认不填写时使用默认分辨率，
              假如默认分辨率的较短的一边像素大于960px，则把短边设置为960，
              假如想识别的图片短边分辨率大于960，则可以手动填写大于960的值，所填写的值越大，识别耗时越久，
              这个参数还和识别准确率有关，如果识别效果不佳，可以调大或者调小这个值，会有不同的识别效果，
            </p>
            <p>
              假如使用自动文本框检测，则推荐文字不要离边界太近，如果边距太小会影响文本框检测的准确率
            </p>
          </div>
        </div>
      </a-col>

      <a-col :lg="3" :md="4" :sm="6">
        <div class="split">
          <div class="divider"></div>
          <div class="btn-group">
            <a-button @click="handleUpload" :loading="isOCRing">点击识别</a-button>
            <!--文字范围 -->
            <div style="margin-top:1rem;">
              <p>
                文字范围:
                <a-switch
                  style="width:auto;min-width:35%;"
                  checked-children="开"
                  un-checked-children="关"
                  @change="changeBoxlistBtn"
                />
              </p>
              <p :hidden="hiddenBoxlistBox">
                <a-input
                  style="width:auto;max-width:100%;"
                  id="compressSizeInput"
                  size="small"
                  v-model="boxList"
                  placeholder="请输入范围列表"
                />
                <!-- @change="onChange" -->
              </p>
            </div>
            <!--白名单 -->
            <div style="margin-top:1rem;">
              <p>
                白名单:
                <a-switch
                  style="width:auto;min-width:35%;"
                  checked-children="开"
                  un-checked-children="关"
                  @change="changeWhitelistBtn"
                />
              </p>
              <p :hidden="hiddenWhitelistBox">
                <a-input
                  style="width:auto;max-width:100%;"
                  id="compressSizeInput"
                  size="small"
                  v-model="whiteList"
                  placeholder="请输入字符串"
                />
                <!-- @change="onChange" -->
              </p>
            </div>
            <!--色偏表 -->
            <div style="margin-top:1rem;">
              <p>
                色偏列表:
                <a-switch
                  style="width:auto;min-width:35%;"
                  checked-children="开"
                  un-checked-children="关"
                  @change="changeColorlistBtn"
                />
              </p>
              <p :hidden="hiddenColorlistBox">
                <a-input
                  style="width:auto;max-width:100%;"
                  id="compressSizeInput"
                  size="small"
                  v-model="colorList"
                  placeholder="请输入色偏列表"
                />
                <!-- @change="onChange" -->
              </p>
            </div>
            <!-- 压缩图片、显示检测后的图片、显示原始值、显示纯文字 default-checked -->
            <div style="margin-top:1rem;">
              <p>
                压缩图片:
                <a-switch
                  style="width:auto;min-width:35%;"
                  checked-children="开"
                  un-checked-children="关"
                  @change="changeCompressBtn"
                />
              </p>
              <p :hidden="hiddenCompressBox">
                压缩尺寸:
                <a-input-number
                  style="width:auto;max-width:45%;"
                  id="compressSizeInput"
                  size="small"
                  v-model="comporessSize"
                  :min="1"
                />
                <!-- @change="onChange" -->
              </p>
            </div>
          </div>

        </div>
      </a-col>

      <a-col :lg="11" :md="10" :sm="9">
        <div class="right-wrapper">
          <div class="detected-img" :hidden="hiddenDetectedImg">
            <a-divider orientation="left">文字检测结果</a-divider>

            <img :src="detectedImg" alt="检测结果图片" />
          </div>

          <div class="ocr-raw" :hidden="hiddenOcrRaw">
            <a-divider orientation="left">原始结果</a-divider>
            <CodeHighlight :txt="ocrRaw" />
          </div>

          <div class="ocr-text" :hidden="hiddenOcrText">
            <a-divider orientation="left">识别的文字</a-divider>
            <CodeHighlight :txt="ocrText" />
          </div>
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import Vue from 'vue'

const axios = require('axios')
import CodeHighlight from '../components/CodeHighlight.vue'
import Message from 'ant-design-vue'
Vue.use(Message)

// 获取上传对象的临时链接
function getObjectURL(file) {
  var url = null
  if (window.createObjectURL != undefined) {
    url = window.createObjectURL(file)
  } else if (window.URL != undefined) {
    // mozilla(firefox)
    url = window.URL.createObjectURL(file)
  } else if (window.webkitURL != undefined) {
    // webkit or chrome
    url = window.webkitURL.createObjectURL(file)
  }
  return url
}

export default {
  name: 'Index',
  data: function() {
    return {
      upImage: '', // 上传后的图片预览地址
      fileList: [], // 上传图片的列表
      detectedImg: '', // 检测后的图片
      ocrRaw: ``, // 返回的原始结果
      ocrText: ``, // 经过提取后的文字结果

      uploading: false, //状态 原生 上传控件的状态
      previewImgHidden: true, // 状态 预览图片是否隐藏
      isOCRing: false, // 状态 是否在识别中
      hiddenDetectedImg: true, //状态  是否显示检测后的图片
      hiddenOcrRaw: true, // 状态  是否显示返回的原始结果
      hiddenOcrText: true, // 状态 是否显示经过提取后的文字结果
      comporessSize: 960,
      whiteList: '',
      colorList: '',
      boxList: '',
      hiddenCompressBox: true,
      hiddenWhitelistBox: true,
      hiddenColorlistBox: true,
      hiddenBoxlistBox: true,
    }
  },
  components: {
    CodeHighlight
  },
  methods: {
    changeCompressBtn(checked) {

      if(checked === true){
        this.$data.hiddenCompressBox = false
      }
      else{
        this.$data.hiddenCompressBox = true
      }
    },
    changeWhitelistBtn(checked) {

      if(checked === true){
        this.$data.hiddenWhitelistBox = false
      }
      else{
        this.$data.hiddenWhitelistBox = true
      }
    },
    changeColorlistBtn(checked) {

      if(checked === true){
        this.$data.hiddenColorlistBox = false
      }
      else{
        this.$data.hiddenColorlistBox = true
      }
    },
    changeBoxlistBtn(checked) {

      if(checked === true){
        this.$data.hiddenBoxlistBox = false
      }
      else{
        this.$data.hiddenBoxlistBox = true
      }
    },
    handleChange(info) {
      const status = info.file.status
      if (status !== 'uploading') {
        this.$data.fileList = [info.file]
        this.$data.upImage = getObjectURL(info.file)
        this.$data.previewImgHidden = false
        console.log('success')
      }
      if (status === 'done') {
        console.log('done')
        this.$message.success(`${info.file.name} file uploaded successfully.`)
      } else if (status === 'error') {
        this.$message.error(`${info.file.name} file upload failed.`)
        console.log('error')
      }
    },
    beforeUpload(file) {
      this.fileList = [file]
      return false
    },
    handleUpload() {
      if (this.fileList.length < 1) {
        this.$message.warning('还没有选择图片')
        return
      }

      const formData = new FormData()
      this.fileList.forEach(file => {
        formData.append('file', file)
      })
      if (this.$data.hiddenCompressBox === false){
        formData.append('compress',this.$data.comporessSize)
      }
      if (this.$data.hiddenWhitelistBox === false){
        formData.append('whitelist',this.$data.whiteList)
      }
      if (this.$data.hiddenColorlistBox === false){
        formData.append('colorlist',this.$data.colorList)
      }
      if (this.$data.hiddenBoxlistBox === false){
        formData.append('boxlist',this.$data.boxList)
      }
      formData.append('isdraw','true')
      this.isOCRing = true
      this.uploading = true

      const _this = this
      axios({
        url: '/api/ocrtext/',
        method: 'post',
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-Requested-With': 'XMLHttpRequest'
        },
        transformRequest: {},
        data: formData
      })
        .then(function(response) {
          _this.$data.detectedImg = response.data['img_detected']

          _this.$data.ocrRaw = ''
          _this.$data.ocrText = ''

          let nextLineHeight = 0 // 下一行的高度

          const words = response.data['words']
          for (let i = 0; i < words.length; i++) {
            _this.$data.ocrRaw += (i+1) + ': ' + JSON.stringify(words[i]) + '\r'

            // 合并同一行的数据
            if (i < words.length - 1) {
              nextLineHeight = words[i + 1][0][1]
              // 判断判断同一行的依据是 两段的行高差 小于 行高的一半
              if (
                Math.abs(words[i][0][1] - nextLineHeight) <
                words[i][0][3] / 2
              ) {
                _this.$data.ocrText += (i+1) + ': ' + words[i][0] + ' '
              } else {
                _this.$data.ocrText += (i+1) + ': ' + words[i][0] + '\r'
              }
            } else {
              _this.$data.ocrText += (i+1) + ': ' + words[i][0]
            }

            // _this.$data.ocrText += raw_data[i][1] + '\r'
          }

          _this.$data.uploading = false
          _this.$data.isOCRing = false
          _this.$data.hiddenDetectedImg = false
          _this.$data.hiddenOcrRaw = false
          _this.$data.hiddenOcrText = false

          _this.$message.success(
            '成功! 耗时：' + response.data['speed_time'] + ' 秒'
          )
        })
        .catch(function(error) {
          // console.log(error)
          _this.$data.isOCRing = false

          const errorInfo = error.response.data['msg'] || error.message
          _this.$message.error('错误：' + errorInfo)

          _this.$data.hiddenDetectedImg = true
          _this.$data.hiddenOcrRaw = true
          _this.$data.hiddenOcrText = true
        })
    }
  },
  watch: {
    fileList: function(newVal, oldVal) {
      if (newVal.length <= 0) {
        this.hiddenDetectedImg = true
        this.hiddenOcrRaw = true
        this.hiddenOcrText = true

        oldVal
      }

    }
  },
  mounted: function() {
    // console.log('mounted')
    this.$nextTick(function() {
      // Code that will run only after the
      // entire view has been rendered

      const _this = this
      document.addEventListener('paste', function(event) {
        var items = event.clipboardData && event.clipboardData.items
        var file = null
        if (items && items.length) {
          // 检索剪切板items
          for (var i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
              file = items[i].getAsFile()
              break
            }
          }
        }

        // console.log(file)
        if (file !== null) {
          _this.$data.fileList = [file]
          _this.$data.upImage = getObjectURL(file)
          _this.$data.previewImgHidden = false
        }
        console.log(_this.$data.fileList)
        // 此时file就是剪切板中的图片文件
      })
    })
  }
}
</script>

<style >
/* >>>>>>  覆盖原生样式 */
.ant-divider-inner-text {
  font-size: 14px;
  color: gray;
}

/* <<<<<<  覆盖原生样式 */

.wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  min-height: 100%;
  height: auto;
}
.left-wrapper {
  min-height: 100vh;
  height: auto;
}
.upimg-dragger {
  height: 4rem;
  margin: 2.5rem 0 1rem 2.5rem;
}
.up-img-preview {
  text-align: center;

  margin: 1.5rem -1rem 1rem 1rem;
}
.up-img-preview img {
  object-fit: contain;
  max-width: 95%;
  max-height: 80vh;
}
.split {
  min-height: 100%;
  /* border: solid gray 1px; */
  height: 100vh;
  position: relative;
}
.divider {
  position: absolute;
  left: 50%;
  top: 0;
  min-height: 100%;
  height: auto;
  width: 1px;
  border-left: 1px solid #d3d3d36b;
}
.btn-group {
  text-align: center;
  margin: 2.5rem 0;
  padding: 1rem;
  background: white;
  width: 100%;
  position: absolute;
}
.btn-group button {
  width: 90%;
}
.right-wrapper {
  padding: 1rem 2.5rem 1rem 0;
}

.detected-img {
  max-height: 50%;
  /* border: 1px solid gray; */
  text-align: center;
}
.detected-img img {
  object-fit: contain;
  max-width: 100%;
  max-height: 40vh;
}
.detected-img .ocr-raw {
  max-height: 40vh;
}
.detected-img .ocr-text {
  max-height: 40vh;
}
</style>
