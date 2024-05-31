-- copied and adapted from https://github.com/dasch-swiss/dsp-api/blob/main/sipi/config/sipi.docker-config.lua

sipi = {
    hostname = '0.0.0.0',
    port = 1024,
    nthreads = 8,
    max_post_size = '2G',
    imgroot = '/sipi/images',
    initscript = '/sipi/scripts/sipi.init.lua',
    tmpdir = '/tmp',
    jwt_secret = 'UP 4888, nice 4-8-4 steam engine',
}

routes = {}
