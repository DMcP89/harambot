
MODULE := harambot

BLUE='\033[0;34m'
NC='\033[0m' # No color

TAG := $(shell git describe --tags --always --abbrev=0)

showenv:
	@echo 'Environment:'
	@echo '-----------------------'
	@echo 'Module:      '${MODULE}
	@echo 'Tag:         '${TAG}

test:
	@python -m pytest -v

run:
	@poetry install
	@python ${MODULE}/bot.py

build-image-dev:
	@echo "${BLUE}Building docker image.."
	@echo "name: ${MODULE}"
	@echo "tag: ${MODULE}:${TAG}${NC}\n"
	@docker buildx debug build --no-cache -t ${MODULE}-dev:${TAG} -f ./docker/Dockerfile.dev .

build-image:
	@echo "${BLUE}Building docker image.."
	@echo "name: ${MODULE}"
	@echo "tag: ${MODULE}:${TAG}${NC}\n"
	@docker build --no-cache -t ${MODULE}:${TAG} -f ./docker/Dockerfile .

run-docker:
	@echo "${BLUE}Running docker image.."
	@echo "name: ${MODULE}"
	@echo "tag: ${MODULE}:${TAG}${NC}\n"
	@docker run --name ${MODULE}\
	 -e DISCORD_TOKEN=${DISCORD_TOKEN}\
	 -e YAHOO_KEY=${YAHOO_KEY}\
	 -e YAHOO_SECRET=${YAHOO_SECRET}\
	 -e DATABASE_URL=${DATABASE_URL}\
	 -e HARAMBOT_KEY=${HARAMBOT_KEY}\
	 -e RUN_MIGRATIONS=${RUN_MIGRATIONS}\
	 -e PORT=10000\
	  --rm ${MODULE}:${TAG}

run-docker-dev:
	@echo "${BLUE}Running docker image.."
	@echo "name: ${MODULE}"
	@echo "tag: ${MODULE}:${TAG}${NC}\n"
	@docker run  --rm --name ${MODULE}-dev\
	 -e DISCORD_TOKEN=${DISCORD_TOKEN}\
	 -e YAHOO_KEY=${YAHOO_KEY}\
	 -e YAHOO_SECRET=${YAHOO_SECRET}\
	 -e DATABASE_URL="sqlite:///dev.harambot.db"\
	 -e RUN_MIGRATIONS=${RUN_MIGRATIONS}\
	 -e HARAMBOT_KEY=${HARAMBOT_KEY}\
	 -e PORT=10000\
	 --cpu-period=50000 --cpu-quota=25000 --memory=512m  ${MODULE}-dev:${TAG}
