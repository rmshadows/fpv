local logFilePath = "/SCRIPTS/FUNCTIONS/test.txt"
local lastTime = 0
local interval = 100  -- 记录间隔 (毫秒) = 0.1秒

-- 初始化日志文件（以追加方式打开）
local function init()
    local file = io.open(logFilePath, "a")
    if file then
        io.write(file, "\n--- Stick Log Started ---\n")
        io.write(file, "Time(ms),CH1,CH2,CH3,CH4\n")
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
            io.write(file, string.format("%d,%d,%d,%d,%d\n", now, ch1, ch2, ch3, ch4))
            io.close(file)
        end
    end
    return 0
end

local function init()
    initLog()
end

return { run = run, init = init }
