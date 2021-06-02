--- 用于调试输出数据的函数，
-- 能够打印出nil,boolean,number,string,table类型的数据，以及table类型值的元表
--  - `data` 表示要输出的数据
--  - `showMetatable` 是否要输出元表,nil表示不输出
--  - `@return` 返回需要输出的字符串
local function M(data, showMetatable)
    local tab_str = {}
    local function _dump(data, showMetatable, lastCount)
        if type(data) ~= 'table' then
            --Value
            if type(data) == 'string' then
                tab_str[#tab_str + 1] = '"'
                tab_str[#tab_str + 1] = data
                tab_str[#tab_str + 1] = '"'
            else
                tab_str[#tab_str + 1] = tostring(data)
            end
        else
            --Format
            local count = lastCount or 0
            count = count + 1
            tab_str[#tab_str + 1] = '{\n'
            --Metatable
            if showMetatable then
                for i = 1, count do
                    tab_str[#tab_str + 1] = '\t'
                end
                local mt = getmetatable(data)
                tab_str[#tab_str + 1] = '"__metatable" = '
                _dump(mt, showMetatable, count) -- 如果不想看到元表的元表，可将showMetatable处填nil
                tab_str[#tab_str + 1] = ',\n' --如果不想在元表后加逗号，可以删除这里的逗号
            end
            --Key
            for key, value in pairs(data) do
                for i = 1, count do
                    tab_str[#tab_str + 1] = '\t'
                end
                if type(key) == 'string' then
                    tab_str[#tab_str + 1] = '"'
                    tab_str[#tab_str + 1] = key
                    tab_str[#tab_str + 1] = '" = '
                elseif type(key) == 'number' then
                    tab_str[#tab_str + 1] = '['
                    tab_str[#tab_str + 1] = key
                    tab_str[#tab_str + 1] = '] = '
                else
                    tab_str[#tab_str + 1] = tostring(key)
                end
                _dump(value, showMetatable, count) -- 如果不想看到子table的元表，可将showMetatable处填nil
                tab_str[#tab_str + 1] = ',\n' --如果不想在table的每一个item后加逗号，可以删除这里的逗号
            end
            --Format
            for i = 1, lastCount or 0 do
                tab_str[#tab_str + 1] = '\t'
            end
            tab_str[#tab_str + 1] = '}'
        end
        --Format
        if not lastCount then
            tab_str[#tab_str + 1] = '\n'
        end
    end
    _dump(data, showMetatable)
    return table.concat(tab_str)
end
return M
