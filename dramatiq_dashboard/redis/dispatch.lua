-- luacheck: globals ARGV KEYS redis unpack
-- dispatch(
--   args=[command, *args],
--   keys=[namespace]
-- )

-- $namespace:__acks__.$worker_id.$queue_name
--   A set of message ids representing fetched-but-not-yet-acked
--   messages belonging to that (worker, queue) pair.
--
-- $namespace:__heartbeats__
--   A sorted set containing unique worker ids sorted by when their
--   last heartbeat was received.
--
-- $namespace:$queue_name
--   A list of message ids.
--
-- $namespace:$queue_name.msgs
--   A hash of message ids -> message data.
--
-- $namespace:$queue_name.XQ
--   A sorted set containing all the dead-lettered message ids
--   belonging to a queue, sorted by when they were dead lettered.
--
-- $namespace:$queue_name.XQ.msgs
--   A hash of message ids -> message data.

local namespace = KEYS[1]
local command = ARGV[1]

-- Command-specific arguments.
local ARGS = {}
for i=2,#ARGV do
    ARGS[i - 1] = ARGV[i]
end

if command == "get_queues_stats" then
    local stats = {}
    for i=1,#ARGS do
        local queue = namespace .. ":" .. ARGS[i]
        local  q_messages = queue .. ".msgs"
        local dq_messages = queue .. ".DQ.msgs"
        local xq_messages = queue .. ".XQ.msgs"

        table.insert(stats, {ARGS[i],
                             redis.call("hlen",  q_messages) or 0,
                             redis.call("hlen", dq_messages) or 0,
                             redis.call("hlen", xq_messages) or 0})
    end

    return stats

elseif command == "get_workers" then
    local heartbeats = namespace .. ":__heartbeats__"
    local cursor = "0"
    local workers = {}
    while true do
        local results = redis.call("zscan", heartbeats, cursor)
        local next_cursor = results[1]
        local worker_ids = results[2]
        if worker_ids then
            for i=1,#worker_ids,2 do
                local id = worker_ids[i]
                local timestamp = worker_ids[i + 1]
                local acks_pattern = namespace .. ":__acks__." .. id .. ".*"
                local acks_keys = redis.call("keys", acks_pattern)
                local total = 0
                for j=1,#acks_keys do
                    total = total + redis.call("scard", acks_keys[j])
                end

                table.insert(workers, {id, timestamp, total})
            end
        end

        if next_cursor == cursor then
            break
        end

        cursor = next_cursor
    end

    return workers

elseif command == "delete_message" then
    local queue = namespace .. ":" .. ARGS[1]
    local queue_messages = queue .. ".msgs"
    local message_id = ARGS[2]

    local tipe = redis.call("type", queue)["ok"]
    if tipe == "zset" then
        redis.call("zrem", queue, 0, message_id)
        redis.call("hdel", queue_messages, message_id)
    else
        redis.call("lrem", queue, 0, message_id)
        redis.call("hdel", queue_messages, message_id)
    end

    -- TODO: maybe remove from ack sets as well?

end
