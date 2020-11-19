
MODULE := harambot

BLUE='\033[0;34m'
NC='\033[0m' # No color

TAG := $(shell git describe --tags --always --dirty)

showenv:
	@echo 'Environment:'
	@echo '-----------------------'
	@echo 'Module:      '${MODULE}
	@echo 'Tag:         '${TAG}

configure:
	@echo 'Creating .secrets.toml file...'
	@test -f config/.secrets.toml || echo '[default]' > config/.secrets.toml
	@echo 'Enter Discord token:' 
	@read DISCORD_TOKEN; echo "DISCORD_TOKEN = '$$DISCORD_TOKEN'" >> config/.secrets.toml;
	@echo 'Enter Yahoo Consumer key:' 
	@read YAHOO_KEY; echo "YAHOO_KEY = '$$YAHOO_KEY'" >> config/.secrets.toml;
	@echo 'Enter Yahoo Consumer secrect:' 
	@read YAHOO_SECRET; echo "YAHOO_SECRET = '$$YAHOO_SECRET'" >> config/.secrets.toml;
	@echo 'Creating guild datastore...'
	@test -f config/guilds.json || echo '{}' > config/guilds.json
	@python ${MODULE}/add_guild.py

test:
	@python -m pytest -v

run:
	@python ${MODULE}/${MODULE}.py

build-docker:
	@echo "${BLUE}Building docker image.."
	@echo "name: ${MODULE}"
	@echo "tag: ${MODULE}:${TAG}${NC}\n"
	@docker build -t ${MODULE}:${TAG} .

run-docker:
	@echo "${BLUE}Running docker image.."
	@echo "name: ${MODULE}"
	@echo "tag: ${MODULE}:${TAG}${NC}\n"
	@docker run ${MODULE}:${TAG} 