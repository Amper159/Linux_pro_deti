# Deployment and development helpers for the Linux pro deti stack.
# Run `make` for the list of targets.
#
#   production:   make init  ->  edit .env  ->  make deploy
#   development:  make dev   (generates .env.dev and ./test_data on its own)

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:
MAKEFLAGS += --no-print-directory
.DEFAULT_GOAL := help

# Which env file the targets work with. `make dev` re-enters make with
# ENV_FILE=.env.dev, so both stacks can run side by side.
ENV_FILE     ?= .env
DEV_ENV_FILE := .env.dev
DEV_DATA     ?= $(CURDIR)/test_data
DEV_PORT     ?= 8099
BACKUP_DIR   ?= $(CURDIR)/backups

# Values from the env file become plain make variables (missing file is fine).
-include $(ENV_FILE)

COMPOSE     := docker compose --env-file $(ENV_FILE)
DEV_COMPOSE := docker compose --env-file $(DEV_ENV_FILE) -f docker-compose.yml -f docker-compose.dev.yml
PROXY       := --profile proxy

APP_URL := http://$(or $(APP_BIND),127.0.0.1):$(or $(APP_PORT),8000)

.PHONY: help init preflight deploy update wait-healthy smoke \
        build up up-proxy down restart ps logs logs-web logs-caddy shell config \
        dev dev-logs dev-shell dev-down dev-clean \
        sandbox-image sandboxes clean-sandboxes backup

help:  ## Show this help
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk -F':.*?## ' '{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

# =============================================================================
#  Production
# =============================================================================

init:  ## Create .env and fill in the values that can be detected locally
	@if [ -f $(ENV_FILE) ]; then
		echo "$(ENV_FILE) already exists - leaving it untouched"
		exit 0
	fi
	cp .env.example $(ENV_FILE)
	secret=$$(python3 -c 'import secrets; print(secrets.token_hex(32))')
	docker_gid=$$(getent group docker | cut -d: -f3 || echo 999)
	sed -i -e "s|^SECRET_KEY=.*|SECRET_KEY=$$secret|" \
		-e "s|^APP_UID=.*|APP_UID=$$(id -u)|" \
		-e "s|^APP_GID=.*|APP_GID=$$(id -g)|" \
		-e "s|^DOCKER_GID=.*|DOCKER_GID=$$docker_gid|" $(ENV_FILE)
	echo "Created $(ENV_FILE) with SECRET_KEY, APP_UID/APP_GID and DOCKER_GID filled in."
	echo "Still to set by hand: SANDBOX_DATA, SITE_ADDRESS, ACME_EMAIL."

preflight:  ## Verify the env file and the host before deploying
	@fail=0
	test -f $(ENV_FILE) || { echo "x $(ENV_FILE) is missing - run: make init"; exit 1; }
	command -v docker >/dev/null || { echo "x docker is not installed"; fail=1; }
	docker compose version >/dev/null 2>&1 || { echo "x docker compose plugin is missing"; fail=1; }
	docker info >/dev/null 2>&1 || { echo "x cannot reach the Docker daemon (is this user in the docker group?)"; fail=1; }
	case "$(SANDBOX_DATA)" in
		/*) ;;
		*) echo "x SANDBOX_DATA must be an absolute path, got '$(SANDBOX_DATA)'"; fail=1 ;;
	esac
	test -n "$(SECRET_KEY)" || echo "! SECRET_KEY is empty - with several workers each may sign cookies differently"
	host_gid=$$(getent group docker | cut -d: -f3 || true)
	if [ -n "$$host_gid" ] && [ "$$host_gid" != "$(DOCKER_GID)" ]; then
		echo "x DOCKER_GID=$(DOCKER_GID) but the host docker group is $$host_gid"
		fail=1
	fi
	$(COMPOSE) $(PROXY) config >/dev/null || fail=1
	if [ $$fail -ne 0 ]; then echo "preflight failed"; exit 1; fi
	echo "ok preflight passed"

deploy: preflight  ## Full production deploy (data dir, images, stack, health check)
	@if [ ! -d "$(SANDBOX_DATA)" ]; then
		if mkdir -p "$(SANDBOX_DATA)" 2>/dev/null; then
			echo "Created $(SANDBOX_DATA)"
		else
			echo "Creating $(SANDBOX_DATA) as root (sudo will ask for your password)"
			sudo mkdir -p "$(SANDBOX_DATA)"
			sudo chown -R $(APP_UID):$(APP_GID) "$(SANDBOX_DATA)"
		fi
	fi
	owner=$$(stat -c '%u:%g' "$(SANDBOX_DATA)")
	if [ "$$owner" != "$(APP_UID):$(APP_GID)" ]; then
		echo "! $(SANDBOX_DATA) is owned by $$owner, expected $(APP_UID):$(APP_GID)"
	fi
	$(MAKE) sandbox-image
	$(COMPOSE) $(PROXY) up -d --build
	$(MAKE) wait-healthy
	$(COMPOSE) $(PROXY) ps
	echo
	echo "Deployed. Public address: $(or $(SITE_ADDRESS),$(APP_URL))"
	echo "Logs: make logs   |  end-to-end check: make smoke (creates a test account)"

update:  ## Pull the latest code, rebuild and restart
	@git pull --ff-only
	$(COMPOSE) $(PROXY) up -d --build
	$(MAKE) wait-healthy
	$(COMPOSE) $(PROXY) ps

wait-healthy:  ## Wait until the app answers on APP_BIND:APP_PORT
	@for i in $$(seq 1 40); do
		if curl -fsS -o /dev/null "$(APP_URL)/" 2>/dev/null; then
			echo "ok app answers at $(APP_URL)"
			exit 0
		fi
		sleep 2
	done
	echo "x app did not answer at $(APP_URL) - see: make logs-web"
	exit 1

smoke:  ## End-to-end check: log in and run a real command in the sandbox
	@jar=$$(mktemp)
	trap 'rm -f "$$jar"' EXIT
	user="smoke-$$$$"
	curl -fsS -o /dev/null -c "$$jar" -H 'Content-Type: application/json' \
		-d "{\"username\":\"$$user\",\"password\":\"smoke1234\"}" \
		"$(APP_URL)/piskoviste/api/login"
	out=$$(curl -fsS -b "$$jar" -H 'Content-Type: application/json' \
		-d '{"command":"echo sandbox-ok; whoami"}' "$(APP_URL)/piskoviste/api/exec")
	if echo "$$out" | grep -q 'sandbox-ok'; then
		echo "ok sandbox runs real commands (account $$user)"
	else
		echo "x smoke test failed: $$out"
		exit 1
	fi

# =============================================================================
#  Development
# =============================================================================

dev: $(DEV_ENV_FILE)  ## Start the local dev stack (own env file, ./test_data, live reload)
	@mkdir -p $(DEV_DATA)
	$(DEV_COMPOSE) up -d --build
	$(MAKE) ENV_FILE=$(DEV_ENV_FILE) wait-healthy
	$(MAKE) ENV_FILE=$(DEV_ENV_FILE) smoke
	echo
	echo "Dev stack ready:  http://127.0.0.1:$(DEV_PORT)"
	echo "Sources are mounted, so saving app.py or sandbox/*.py reloads gunicorn."
	echo "Logs: make dev-logs  |  stop: make dev-down  |  wipe test data: make dev-clean"

# Generated once; delete it to regenerate with different values.
$(DEV_ENV_FILE): .env.example
	@cp .env.example $@
	docker_gid=$$(getent group docker | cut -d: -f3 || echo 999)
	sed -i -e "s|^SECRET_KEY=.*|SECRET_KEY=$$(python3 -c 'import secrets; print(secrets.token_hex(16))')|" \
		-e "s|^SANDBOX_DATA=.*|SANDBOX_DATA=$(DEV_DATA)|" \
		-e "s|^APP_UID=.*|APP_UID=$$(id -u)|" \
		-e "s|^APP_GID=.*|APP_GID=$$(id -g)|" \
		-e "s|^DOCKER_GID=.*|DOCKER_GID=$$docker_gid|" \
		-e "s|^APP_BIND=.*|APP_BIND=127.0.0.1|" \
		-e "s|^APP_PORT=.*|APP_PORT=$(DEV_PORT)|" \
		-e "s|^WEB_CONCURRENCY=.*|WEB_CONCURRENCY=1|" \
		-e "s|^SANDBOX_IMAGE=.*|SANDBOX_IMAGE=linux-pro-deti-sandbox:dev|" \
		-e "s|^SITE_ADDRESS=.*|SITE_ADDRESS=:80|" \
		-e "s|^ACME_EMAIL=.*|ACME_EMAIL=|" $@
	printf '\n# Added by `make dev`: keeps the dev stack separate from production.\nENV_FILE=%s\nCOMPOSE_PROJECT_NAME=linux-pro-deti-dev\n' "$@" >> $@
	echo "Generated $@ for local development"

dev-logs:  ## Follow the dev stack logs
	@$(DEV_COMPOSE) logs -f --tail 100

dev-shell:  ## Open a shell in the dev container
	@$(DEV_COMPOSE) exec web /bin/sh

dev-down:  ## Stop the dev stack (test data is kept)
	@$(DEV_COMPOSE) down

dev-clean: dev-down  ## Stop the dev stack and delete ./test_data and .env.dev
	@docker ps -aq --filter name=lpd-piskoviste- | xargs -r docker rm -f
	rm -rf $(DEV_DATA) $(DEV_ENV_FILE)
	echo "Development leftovers removed"

# =============================================================================
#  Everyday operations
# =============================================================================

config:  ## Validate docker-compose.yml against the current env file
	@$(COMPOSE) $(PROXY) config >/dev/null && echo "compose config OK"

build:  ## Build the application image
	@$(COMPOSE) build

up:  ## Start the app only (reverse proxy provided elsewhere)
	@$(COMPOSE) up -d --build

up-proxy:  ## Start the app together with Caddy (automatic HTTPS)
	@$(COMPOSE) $(PROXY) up -d --build

down:  ## Stop the stack (volumes and user data are kept)
	@$(COMPOSE) $(PROXY) down

restart:  ## Restart the running containers
	@$(COMPOSE) $(PROXY) restart

ps:  ## Show the stack status
	@$(COMPOSE) $(PROXY) ps

logs:  ## Follow logs of every service
	@$(COMPOSE) $(PROXY) logs -f --tail 100

logs-web:  ## Follow application logs
	@$(COMPOSE) logs -f --tail 100 web

logs-caddy:  ## Follow reverse proxy logs
	@$(COMPOSE) $(PROXY) logs -f --tail 100 caddy

shell:  ## Open a shell in the running application container
	@$(COMPOSE) exec web /bin/sh

# =============================================================================
#  Sandbox and data
# =============================================================================

sandbox-image:  ## Pre-build the sandbox image so the first user waits less
	@docker build -t $(or $(SANDBOX_IMAGE),linux-pro-deti-sandbox:2) sandbox/docker

sandboxes:  ## List the running per-user sandbox containers
	@docker ps --filter name=lpd-piskoviste- \
		--format 'table {{.Names}}\t{{.Status}}\t{{.Size}}'

clean-sandboxes:  ## Remove all sandbox containers (home directories survive)
	@docker ps -aq --filter name=lpd-piskoviste- | xargs -r docker rm -f
	echo "Sandbox containers removed"

backup:  ## Archive SANDBOX_DATA into BACKUP_DIR (accounts, homes, progress)
	@mkdir -p $(BACKUP_DIR)
	tar -czf $(BACKUP_DIR)/sandbox_data-$$(date +%Y%m%d-%H%M%S).tar.gz \
		-C $$(dirname $(SANDBOX_DATA)) $$(basename $(SANDBOX_DATA))
	ls -lh $(BACKUP_DIR) | tail -1
