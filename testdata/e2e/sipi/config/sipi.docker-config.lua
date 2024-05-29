--
-- This config file is used for the testcontainers of the e2e tests.
-- Copied and adapted from https://github.com/dasch-swiss/dsp-api/blob/main/sipi/config/sipi.docker-config.lua
--
sipi = {
    hostname = '0.0.0.0',
    port = 1024,
    nthreads = 8,
    jpeg_quality = 60,
    scaling_quality = {
        jpeg = "medium",
        tiff = "high",
        png = "high",
        j2k = "high"
    },
    keep_alive = 5,
    max_post_size = '2G',
    imgroot = '/sipi/images', -- make sure that this directory exists
    prefix_as_path = true,
    subdir_levels = 0,
    subdir_excludes = { "knora" },
    initscript = '/sipi/scripts/sipi.init.lua',
    cachedir = '/sipi/cache',
    cachesize = '100M',
    cache_hysteresis = 0.15,
    scriptdir = '/sipi/scripts',
    thumb_size = '!128,128',
    tmpdir = '/tmp',
    max_temp_file_age = 86400,
    knora_path = 'api',
    knora_port = '3333',
    jwt_secret = 'UP 4888, nice 4-8-4 steam engine',
    loglevel = "DEBUG"
}


fileserver = {
    docroot = '/sipi/server',
    wwwroute = '/server'
}

routes = {}
