require("TSLib")
local dump = require("DumpData")

local ocrapi = require("ocrapi")
---会在res目录下创建 item_ocr 目录,用于存放临时截图文件,文件名为 item.jpg
local itemocr = ocrapi.new("http://192.168.10.2:8099/api/ocrtext/","item")


--- 这里使用数组的形式,返回值将会是{识别到的内容}
local item = {
    {237,136,301,162},
    {90,278,146,298},
    {399,279,436,292},
}
--- 返回内容:
-- {
--     {"这是一个识别测试1"},
--     {"这是一个识别测试2"},
--     {"这是一个识别测试3"},
-- }
local words = itemocr:ocr(item)
for index, value in ipairs(words) do
    nLog(index..": "..value[1])
end
