-- tarantool/init.lua
-- Tarantool instance configuration for PrizeRace.
-- This file is mounted into the container by docker-compose.

box.cfg {
    listen           = '0.0.0.0:3301',
    log_level        = 5,         -- INFO
    memtx_memory     = 256 * 1024 * 1024,  -- 256 MB
    vinyl_memory     = 128 * 1024 * 1024,
    work_dir         = '/var/lib/tarantool',
    checkpoint_count = 2,
    checkpoint_interval = 3600,   -- snapshot every hour
}

-- Grant guest access for the Python driver (no auth in dev)
-- In production, create a dedicated user with a password and
-- set TARANTOOL_USER / TARANTOOL_PASSWORD in the environment.
box.once('init_guest', function()
    box.schema.user.grant('guest', 'read,write,execute', 'universe',
        nil, {if_not_exists = true})
end)

-- Spaces are bootstrapped by the Python app on startup via box.once('prize_race_v1', ...)
-- No need to define them here — the app owns the schema.

print("Tarantool PrizeRace instance started on 3301")
