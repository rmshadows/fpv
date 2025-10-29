local logFilePath = ""  -- 文件名
local lastTime = 0      -- 上次记录的时间
local interval = 33.33  -- 记录间隔 (毫秒)  相当于30帧
local restTime = 300    -- 休息时间，如果disarm超过这么多毫秒，就另启新log文件记录摇杆日志

-- 新增日志文件
local function makeNewFile()
    local date = getDateTime()
    logFilePath = string.format("/LOGS/stk_%04d%02d%02d_%02d%02d%02d.log", date.year, date.mon, date.day, date.hour, date.min, date.sec)

    local file = io.open(logFilePath, "a")
    if file then
        io.write(file, "Ail,Ele,Thr,Rud,Time\n")
        io.close(file)
    else
        return false
    end
    return true
end

-- 记录摇杆数据
local function recordLog()
    local ch1 = getValue("ch1")
    local ch2 = getValue("ch2")
    local ch3 = getValue("ch3")
    local ch4 = getValue("ch4")

    local file = io.open(logFilePath, "a")
    if file then
        -- 获取当前时间
        local time = getDateTime()
        local timeHHMMSS = string.format("%02d:%02d:%02d", time.hour, time.min, time.sec) -- 格式如 15:23:59

        io.write(file, string.format("%d,%d,%d,%d,%s\n", ch1, ch2, ch3, ch4, timeHHMMSS))
        io.close(file)
    end
end

-- 该Model初加载时执行一次
local function init()
    -- Do nothing when initialized
end

-- 主循环，每帧调用
local function run()
    local now = getTime() * 10  -- getTime() 返回0.01s为单位
    if now - lastTime >= restTime then
        lastTime = now

        makeNewFile()
    elseif now - lastTime >= interval then
        lastTime = now

        recordLog()
    end
    return 0
end

return { run = run, init = init }
