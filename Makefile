
MODULE := harambot

BLUE='\033[0;34m'
NC='\033[0m' # No color

TAG := $(shell git describe --tags --always)

showenv:
	@echo 'Environment:'
	@echo '-----------------------'
	@echo 'Module:      '${MODULE}
	@echo 'Tag:         '${TAG}

test:
	@python -m pytest -v

run:
	@pip install -r requirements.txt
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
