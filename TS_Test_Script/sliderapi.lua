require('TSLib')
local ts = require('ts')
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
--- @param url string @必填,接口地址 'http://ip:port/api/slider/',默认端口8099
function M.new(url)
    local obj = {}
    -- 确保临时文件存储的文件夹存在
    obj.path = userPath().."/res/slider/"
    obj.url = url
    do
        local bool = isFileExist(obj.path)
        if not bool then
            os.execute("mkdir "..obj.path)
        end
    end
    obj.img_path = obj.path.."slider.jpg"
    -- dialog(obj.img_path)

    ---创建一个返回滑块的识别
    --- @param box table @必填 格式如{x1,y1,x2,y2}
    function obj:find(box)
        local imgfile
        -- dialog(self.img_path)
        if type(box) == "string" then
            local file = io.open(box, 'rb')
            if file then
                imgfile = file:read('*a')
                file:close()
            else
                logger:error("识别API图片打开失败")
                return
            end
        elseif type(box) == "table" then
            local x1,y1,x2,y2 = table.unpack(box)
            snapshot(self.img_path,x1,y1,x2,y2)
            local file = io.open(self.img_path, 'rb')
            if file then
                imgfile = file:read('*a')
                file:close()
            else
                logger:error("识别API图片打开失败")
                return
            end
        else
            
            return
        end

        local data = string.format(
            '----abcdefg\r\nContent-Disposition: form-data; name="file"; filename="push.jpg"\r\nContent-Type: image/jpeg\r\n\r\n%s\r\n----abcdefg--',
            imgfile)
        local headers = {
            ['Content-Type'] = 'multipart/form-data; boundary=--abcdefg',
            ['Content-Length'] = #data
        }
        local response_body = {}
        local _, code =
            http_socket.request {
            url = self.url,
            method = 'POST',
            headers = headers,
            source = ltn12.source.string(data),
            sink = ltn12.sink.table(response_body)
        }

        if code == 200 then
            local str = table.concat(response_body)
            if #str > 0 then
                local points = json.decode(str)["res"]
                -- dialog(str)
                if points then
                    return points[1],points[2]
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
