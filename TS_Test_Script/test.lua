require("TSLib")

local ocrapi = require("ocrapi")
---会在res目录下创建 item_ocr 目录,用于存放临时截图文件,文件名为 item.jpg
local itemocr = ocrApi.new("http://192.168.1.2:8089/api/ocrtext/","item")


--- 这里使用key,value模式,返回值将会是{key=识别到的内容}
local item = {
    ["历练"] = {237,136,301,162},
    ["密地"] = {97,280,139,294},
    ["豪侠"] = {375,722,419,744}
}
--- 返回内容:
-- {
--     ["历练"] = 25,
--     ["密地"] = 45,
--     ["豪侠"] = 12
-- }
local words = itemocr:ocr(item,"1234567890/")
for key, value in pairs(words) do
    nLog(key..": "..value)
end

--- 这里使用数组的形式,返回值将会是{识别到的内容}
local item = {
    {237,136,301,162},
    {90,278,146,298},
    {399,279,436,292},
}
--- 返回内容:
-- {
--     "这是一个识别测试1",
--     "这是一个识别测试2",
--     "这是一个识别测试3",
-- }
local words = itemocr:ocr(item)
for index, value in ipairs(words) do
    nLog(index..": "..value)
end
