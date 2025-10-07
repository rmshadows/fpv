local logFilePath = "/SCRIPTS/FUNCTIONS/test.log"
local lastTime = 0
local interval = 33.33  -- 记录间隔 (毫秒)  相当于30帧

-- 初始化日志文件（以追加方式打开）
local function init()
    local file = io.open(logFilePath, "a")
    if file then
        io.write(file, "\nAil,Ele,Thr,Rud\n")
        io.close(file)
    else
        return false
    end
    return true
end

-- 主循环，每帧调用
local function run()
    local now = getTime() * 10  -- getTime() 返回0.01s为单位
    if now - lastTime >= interval then
        lastTime = now

        local ch1 = getValue("ch1")
        local ch2 = getValue("ch2")
        local ch3 = getValue("ch3")
        local ch4 = getValue("ch4")

        local file = io.open(logFilePath, "a")
        if file then
            io.write(file, string.format("%d,%d,%d,%d\n", ch1, ch2, ch3, ch4))
            io.close(file)
        end
    end
    return 0
end

return { run = run, init = init }
