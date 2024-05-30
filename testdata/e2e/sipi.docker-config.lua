--
-- This config file is used for the testcontainers of the e2e tests.
-- Copied and adapted from https://github.com/dasch-swiss/dsp-api/blob/main/sipi/config/sipi.docker-config.lua
--
sipi = {
    hostname = '0.0.0.0',
    port = 1024,
    nthreads = 8,
    jpeg_quality = 60,
    keep_alive = 5,
    max_post_size = '2G',
    imgroot = '/sipi/images',
    prefix_as_path = true,
    subdir_levels = 0,
    subdir_excludes = { "knora" },
    initscript = '/sipi/scripts/sipi.init.lua',
    scriptdir = '/sipi/scripts',
    thumb_size = '!128,128',
    tmpdir = '/tmp',
    jwt_secret = 'UP 4888, nice 4-8-4 steam engine',
    loglevel = "DEBUG"
}

routes = {}
