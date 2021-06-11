require('TSLib')
local ts = require('ts')
local sz = require("sz")
local image = require("tsimg")
local json = ts.json
local http_socket = require('socket.http')

-- logger日志,如有需要自行接入.
local logger = {}
function logger:error(msg)
    nLog(msg)
end
function logger:debug(msg)
    nLog(msg)
end


local M = {}
--- 创建一个新的接口,会在触动res目录下创建临时截图文件
--- @param url string @必填,接口地址 'http://ip:port/api/ocrtext/',默认端口8099
--- @param filename string  @选填,文件名,用于res目录下临时文件的文件名.
function M.new(url,filename)
    local obj = {}
    if not filename then
        obj.filename = "ocr_img"
    else
        obj.filename = filename
    end
    -- 确保临时文件存储的文件夹存在
    obj.path = userPath().."/res/ocr_"..filename.."/"
    obj.subpath = obj.path.."sub_img/"
    obj.suffix = ".jpg"
    obj.img_path = table.concat{obj.path,obj.filename,obj.suffix}
    do
        local bool = isFileExist(obj.path)
        if not bool then
            os.execute("mkdir "..obj.path)
        end
        bool = isFileExist(obj.subpath)
        if not bool  then
            os.execute("mkdir "..obj.subpath)
        end
    end

    ---识别方法,向接口请求识别文字
    --- @param box table @必填,有两种填写方式:
    -- - 一维数组是查找模式,查找屏幕范围的所有文字,(服务在查找过程中包含文本框识别).如{x1,y1,x2,y2}
    -- - 二维数组是识别模式,识别所标注的文本框范围内的文字,如{{x1,y1,x2,y2},{x1,y1,x2,y2}...}
    --- @param opts table @选填,可选项,格式为{whitelist="测试",colorlist={{0x000000,0x000011},{0x111111}...}},compress=960}
    -- - whitelist 白名单字符串.
    -- - colorlist 颜色偏色列表,仅查找给出的颜色列表的文字.
    -- - compress 图像压缩比,把图像的短边(图像中较短的边长)压缩成对应数值进行查找.
    -- 不填写时短边大于960时,压缩成960,否则不压缩,注意!!!该参数会影响文本框的识别,
    -- 比如在图像较大,文字较小时,可以调整参数,提高准确率,参数越小,速度越快.一般情况可以不填写,或者填写nil
    function obj:ocr(box,opts)
        if type(box) ~= "table" then
            return
        end
        local whitelist = opts.whitelist or nil
        local colorlist = opts.colorlist or nil
        local compress = opts.compress or nil
        local imgfile,boxlist
        if type(box[1]) == "table" then
            local sub_img = {}
            local box_tmp = {}
            local box_key = {}
            keepScreen(true)
            for k, v in ipairs(box) do
                local x1,y1,x2,y2 = table.unpack(v)
                local path = table.concat{self.subpath,self.filename,k,self.suffix}
                snapshot(path,x1,y1,x2,y2)
                sub_img[#sub_img+1] = path
                if #box_key == 0 then
                    box_tmp[k] = {0,0,x2-x1,y2-y1}
                else
                    box_tmp[k] = {0,box_tmp[box_key[#box_key]][4]+1,x2-x1,box_tmp[box_key[#box_key]][4]+1+y2-y1}
                end
                box_key[#box_key+1] = k
            end
            keepScreen(false)
            box = nil
            local bool,msg = image.operMerge(sub_img, self.img_path ,1)
            if not bool then
                logger:error("识别API合成图片失败: "..msg)
                return
            end
            boxlist = box_tmp
        else
            local x1,y1,x2,y2 = table.unpack(box)
            snapshot(self.img_path,x1,y1,x2,y2)
        end
        
        local file = io.open(self.img_path, 'rb')
        if file then
            imgfile = file:read('*a')
            file:close()
        else
            logger:error("识别API图片打开失败")
            return
        end

        local data = {}
        if boxlist then
            data[#data+1] = string.format('----abcdefg\r\nContent-Disposition: form-data; name="boxlist"\r\n\r\n%s\r\n',json.encode(boxlist))
        elseif compress then
            data[#data+1] = string.format('----abcdefg\r\nContent-Disposition: form-data; name="compress"\r\n\r\n%s\r\n',compress)
        end
        if whitelist then
            data[#data+1] = string.format('----abcdefg\r\nContent-Disposition: form-data; name="whitelist"\r\n\r\n%s\r\n',whitelist)
        end
        if colorlist then
            data[#data+1] = string.format('----abcdefg\r\nContent-Disposition: form-data; name="colorlist"\r\n\r\n%s\r\n',json.encode(colorlist))
        end
        data[#data+1] = string.format(
            '----abcdefg\r\nContent-Disposition: form-data; name="file"; filename="push.jpg"\r\nContent-Type: image/jpeg\r\n\r\n%s\r\n----abcdefg--',
            imgfile)
        data = table.concat(data)
        local headers = {
            ['Content-Type'] = 'multipart/form-data; boundary=--abcdefg',
            ['Content-Length'] = #data
        }
        local response_body = {}
        local _, code =
            http_socket.request {
            url = url,
            method = 'POST',
            headers = headers,
            source = ltn12.source.string(data),
            sink = ltn12.sink.table(response_body)
        }

        if code == 200 then
            local str = table.concat(response_body)
            if #str > 0 then
                local words = json.decode(str)["words"]
                if words then
                    local res = {}
                    if boxlist then
                        for _,v in ipairs(words) do
                            table.insert(res,{v[1]})
                        end
                    else
                        local x1,y1,x2,y2 = table.unpack(box)
                        for _,v in ipairs(words) do
                            table.insert(res,{v[1],{v[2][1]+x1,v[2][2]+y1,v[2][3]+x1,v[2][4]+y1}})
                        end
                    end
                    return res
                else
                    logger:debug("识别API识别内容失败: "..response_body[1])
                    return
                end
            end
        else
            logger:error("识别API连接失败: "..response_body[1],self.img_path)
            return
        end
    end

    return obj
end

return M
