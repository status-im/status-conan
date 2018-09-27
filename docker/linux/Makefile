GIT_COMMIT = $(shell git rev-parse --short HEAD)

IMAGE_TAG = $(GIT_COMMIT)
IMAGE_NAME = statusteam/linux-conan-ubuntu:$(IMAGE_TAG)

# This is a code for automatic help generator.
# It supports ANSI colors and categories.
# To add new item into help output, simply add comments
# starting with '##'. To add category, use @category.
GREEN  := $(shell tput -Txterm setaf 2)
WHITE  := $(shell tput -Txterm setaf 7)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)
HELP_FUN = \
		   %help; \
		   while(<>) { push @{$$help{$$2 // 'options'}}, [$$1, $$3] if /^([a-zA-Z\-]+)\s*:.*\#\#(?:@([a-zA-Z\-]+))?\s(.*)$$/ }; \
		   print "Usage: make [target]\n\n"; \
		   for (sort keys %help) { \
			   print "${WHITE}$$_:${RESET}\n"; \
			   for (@{$$help{$$_}}) { \
				   $$sep = " " x (32 - length $$_->[0]); \
				   print "  ${YELLOW}$$_->[0]${RESET}$$sep${GREEN}$$_->[1]${RESET}\n"; \
			   }; \
			   print "\n"; \
		   }

help: ##@other Show this help
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

build-qt: ##@build Build MXE toolchain and QT5 without webkit
	docker build \
		--build-arg="GIT_COMMIT=$(GIT_COMMIT)" \
		--label="qt5 commit=$(GIT_COMMIT)" \
		-t $(IMAGE_NAME) .

build-qt-with-webkit: ##@build Build MXE toolchain and QT5 with webkit
	docker build \
		--build-arg="GIT_COMMIT=$(GIT_COMMIT)" \
		--build-arg="QT_OPTIONS=webkit=True" \
		--label="qt5-webkit commit=$(GIT_COMMIT)" \
		-t $(IMAGE_NAME) .

push-%: ##@remote Push all built images to remote
	${MAKE} build-$*
	docker run -ti $(IMAGE_NAME) make push

dump-logs: ##@build Dump Conan trace logs
	docker run -ti $(IMAGE_NAME) cat /tmp/conan_trace.log

remove-image:
	docker rmi $(IMAGE_NAME)
