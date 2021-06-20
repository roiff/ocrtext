-- require("TSLib")
-- local dump = require("DumpData")

-- local ocrapi = require("ocrapi")
-- ---会在res目录下创建 item_ocr 目录,用于存放临时截图文件,文件名为 item.jpg
-- local itemocr = ocrapi.new("http://192.168.10.2:8099/api/ocrtext/","item")


-- --- 这里使用数组的形式,返回值将会是{识别到的内容}
-- local item = {
--     {237,136,301,162},
--     {90,278,146,298},
--     {399,279,436,292},
-- }
-- --- 返回内容:
-- -- {
-- --     {"这是一个识别测试1"},
-- --     {"这是一个识别测试2"},
-- --     {"这是一个识别测试3"},
-- -- }
-- local words = itemocr:ocr(item)
-- for index, value in ipairs(words) do
--     nLog(index..": "..value[1])
-- end

-- --完整的写法,识别
-- local item = {
--     {237,136,301,162},
--     {90,278,146,298},
--     {399,279,436,292},
-- }
-- local opts = {
--     whitelist = "01234567890",
--     colorlist = {{}},
-- }
-- local words = itemocr:ocr(item,opts)


local ddd = require("sliderapi")
local slider = ddd.new("http://47.92.105.212:8099/api/slider/")

fwShowWnd("window1",27,159,612,688,0);

-- local stsrt_x,end_x = slider.find("/mnt/sdcard/TouchSprite/res/1623310716.png")
for i = 1,10 do
    fwShowImageView("window1","picid1","1.png",20,20,200,200) 
    local stsrt_x,end_x = slider:find({27,159,612,688})
    
    fwShowButton("window1","bn","","FFFFFF","FF0000","",15,end_x,0,end_x+3,360)
    fwShowButton("window1","button1","继续","FFFFFF","FF0000","",15,260,529-95,320,529-40)
    while (true) do
        local vid,kind = fwGetPressedButton();
        if vid == "button1" then
                break
        end
    end
end

local Qrcode = require("qrcodeapi")
local qrcode = Qrcode.new("http://47.92.105.212:8099/api/qrcode/")


dialog(qrcode:find({27,159,612,688}))
