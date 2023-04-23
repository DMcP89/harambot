
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
	@pip install -r requirements.txt
	@python ${MODULE}/bot.py

build-image:
	@echo "${BLUE}Building docker image.."
	@echo "name: ${MODULE}"
	@echo "tag: ${MODULE}:${TAG}${NC}\n"
	@docker build -t ${MODULE}:${TAG} .

run-docker:
	@echo "${BLUE}Running docker image.."
	@echo "name: ${MODULE}"
	@echo "tag: ${MODULE}:${TAG}${NC}\n"
	@docker run --name ${MODULE}\
	 -e DISCORD_TOKEN=${DISCORD_TOKEN}\
	 -e YAHOO_KEY=${YAHOO_KEY}\
	 -e YAHOO_SECRET=${YAHOO_SECRET}\
	 -e DATABASE_URL=${DATABASE_URL}\
	 -e RUN_MIGRATIONS=${RUN_MIGRATIONS}\
	  --rm ${MODULE}:${TAG}
