require('TSLib')
local ts = require('ts')
local image = require("tsimg")
local json = ts.json
local http_socket = require('socket.http')

--logger日志,如有需要自行接入.
local logger = {}
function logger:error(msg)
    nLog(msg)
end
function logger:debug(msg)
    nLog(msg)
end


local M = {}
--- 创建一个新的接口,会在触动res目录下创建临时截图文件
-- - @url 必填,接口地址 'http://ip:port/api/ocrtext/',默认端口8099
-- - @filename 选填,文件名,用于res目录下临时文件的文件名.
-- - @suffix 选填,后缀,默认为.jpg,可以修改为.png
function M.new(url,filename,suffix)
    local obj = {}
    if not filename then
        obj.filename = "ocr_img"
    else
        obj.filename = filename
    end
    
    obj.path = userPath().."/res/ocr_"..filename.."/"
    obj.findimg = userPath().."/res/find_"..filename.."/"
    obj.subpath = obj.path.."sub_img/"
    obj.suffix = suffix or ".jpg"
    do
        local bool = isFileExist(obj.path)
        if not bool then
            os.execute("mkdir "..obj.path)
        end
        bool = isFileExist(obj.findimg)
        if not bool then
            os.execute("mkdir "..obj.findimg)
        end
        bool = isFileExist(obj.subpath)
        if not bool  then
            os.execute("mkdir "..obj.subpath)
        end
    end
    
    ---识别方法,向接口请求识别文字
    -- - @box 必填,屏幕中要识别的文本框范围,是一个二维数组新式,如{{x1,y1,x2,y2},{x1,y1,x2,y2}}
    -- 也可以使用key,value形式,如{["测试1"]={x1,y1,x2,y2}}
    -- - @whitelist 选填,白名单字符串.
    function obj:ocr(box,whitelist)
        local sub_img = {}
        local box_tmp = {}
        local box_key = {}
        keepScreen(true)
        for k, v in pairs(box) do
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
        local img_path = table.concat{self.path,self.filename,self.suffix}
        local bool,msg = image.operMerge(sub_img, img_path ,1)
        if not bool then
            logger:error("识别API合成图片失败: "..msg)
            return
        end

        local imgfile
        local file = io.open(img_path, 'rb')
        if file then
            imgfile = file:read('*a')
            file:close()
        else
            logger:error("识别API图片打开失败")
            return
        end

        local data = {}
        data[1] = string.format('----abcdefg\r\nContent-Disposition: form-data; name="boxarr"\r\n\r\n%s\r\n',json.encode(box_tmp))
        if whitelist then
            data[#data+1] = string.format('----abcdefg\r\nContent-Disposition: form-data; name="whitelist"\r\n\r\n%s\r\n',whitelist)
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
                    return words
                else
                    logger:debug("识别API识别内容失败: "..response_body[1])
                    return
                end
            end
        else
            logger:error("识别API连接失败: "..response_body[1],img_path)
            return
        end
    end

    function obj:find(box,whitelist,compress)
        local x1,y1,x2,y2 = table.unpack(box)
        
        local img_path = table.concat{self.findimg,self.filename,self.suffix}
        snapshot(img_path,x1,y1,x2,y2)

        local imgfile
        local file = io.open(img_path, 'rb')
        if file then
            imgfile = file:read('*a')
            file:close()
        else
            logger:error("识别API图片打开失败")
            return
        end

        local data = {}
        data[1] = ''
        if whitelist then
            data[#data+1] = string.format('----abcdefg\r\nContent-Disposition: form-data; name="whitelist"\r\n\r\n%s\r\n',whitelist)
        end
        if compress and type(compress) == 'number' then
            data[#data+1] = string.format('----abcdefg\r\nContent-Disposition: form-data; name="compress"\r\n\r\n%s\r\n',compress)
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
                    return words
                else
                    logger:debug("识别API识别内容失败: "..response_body[1])
                    return
                end
            end
        else
            logger:error("识别API连接失败: "..response_body[1],img_path)
            return
        end
    end

    return obj
end

return M
