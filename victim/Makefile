DOCKER:=@docker
APP_NAME=maissacrement/docker/sideattack
VERSION=$(shell git rev-parse --short HEAD)
DOCKER_REPO=registry.gitlab.com
PWD:=`pwd`

env:=.env
-include $(env)

build:
	${DOCKER} build -t ${APP_NAME} . --file ./NOC.Dockerfile

xserver-dev: build
	xhost + # give foward auth
	${DOCKER} run --rm -it --privileged \
		--env "TERM=xterm-256color" \
		-v /dev/bus/usb:/dev/bus/usb \
		-v /var/run/dbus/:/var/run/dbus/ \
		--cap-add=SYS_ADMIN --cap-add=NET_ADMIN \
		--net=host \
	${APP_NAME} /bin/bash -c "entrypoint.sh"
	xhost -