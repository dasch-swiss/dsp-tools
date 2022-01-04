UNAME := $(shell uname)
ifeq ($(UNAME),Darwin)
  DOCKERHOST :=  $(shell ifconfig en0 | grep inet | grep -v inet6 | cut -d ' ' -f2)
else
  DOCKERHOST := $(shell ip -4 addr show docker0 | grep -Po 'inet \K[\d.]+')
endif
