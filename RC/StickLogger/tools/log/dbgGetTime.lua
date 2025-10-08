--[[
EdgetX getTime() 调试脚本
用途：
  - 检测不同遥控器设备 getTime() 的精度和稳定性
  - 输出每帧间隔 delta 和累计时间 elapsed 到 log 文件
使用：
  - 上传到遥控器 /SCRIPTS/FUNCTIONS/debug_time.lua
  - 在模型中加载并运行
  - log 文件：/SCRIPTS/FUNCTIONS/debug_time.log
]]

local lastTime = getTime() * 10  -- 毫秒
local t_start = lastTime
local frameCount = 0
local logFilePath = "/SCRIPTS/FUNCTIONS/debug_time.log"

-- 清空旧日志文件
local function initLog()
    local file = io.open(logFilePath, "w")
    if file then
        io.write(file, "Frame,Delta(ms),Elapsed(ms)\n")
        io.close(file)
    end
end

initLog()

local function run()
    frameCount = frameCount + 1
    local now = getTime() * 10  -- 转成毫秒
    local delta = now - lastTime
    local elapsed = now - t_start
    lastTime = now

    -- 写入 log 文件
    local file = io.open(logFilePath, "a")
    if file then
        io.write(file, string.format("%d,%.2f,%.2f\n", frameCount, delta, elapsed))
        io.close(file)
    end

    -- 每 20 帧打印一次到遥控器屏幕（可选）
    if frameCount % 20 == 0 then
        print(string.format("Frame %d: delta = %.2f ms, elapsed = %.2f ms", frameCount, delta, elapsed))
    end

    return 0
end

local function init()
    -- 初始化时清空时间计数
    lastTime = getTime() * 10
    t_start = lastTime
    frameCount = 0
end

return { run = run, init = init }
