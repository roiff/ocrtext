require("TSLib")
local dump = require("DumpData")

local ocrapi = require("ocrapi")
---会在res目录下创建 item_ocr 目录,用于存放临时截图文件,文件名为 item.jpg
local itemocr = ocrapi.new("http://47.92.105.212:8099/api/","item")


--- 这里使用key,value模式,返回值将会是{key=识别到的内容}
local item = {
    ["历练"] = {237,136,301,162},
    ["密地"] = {97,280,139,294},
    ["豪侠"] = {375,722,419,744}
}
-- - 返回内容:
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


-- 查找接口使用

local box = {5,79,500,700}  -- 要识别的文字的屏幕区域
local w = "集市"  -- 要识别的文字白名单
local words1 = itemocr:find(box) -- 在范围内查找所有查找到的字符串,返回格式 {{"文字内容1",{1,1,5,5}},{"文字内容2",{10,10,50,50}}
local str= dump(words1)
nLog(str)

local words2 = itemocr:find(box,w) -- 在范围内查找查找到的字符串,并匹配字符串在"集市"(白名单)范围内
local str= dump(words1)
nLog(str)

local words3 = itemocr:find(box,w,608) -- 在范围内查找查找到的字符串,并匹配字符串在"集市"(白名单)范围内,并把图像的短边压缩(放大)到608分辨率进行识别.
local str= dump(words1)
nLog(str)

local words3 = itemocr:find(box,w,nil,true) -- 在范围内查找查找到的字符串,并匹配字符串为"集市"(白名单)的字符串,单个"集"就不会返回.
local str= dump(words1)
nLog(str)
