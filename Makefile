.PHONY: validate build up down restart logs health test-tool ps audit jobs create-job shell clean

validate:
	python3 -m py_compile agent/*.py
	docker compose config

build:
	docker compose build

up:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f --tail=150

health:
	curl -s http://127.0.0.1:8080/health | jq

ps:
	curl -s http://127.0.0.1:8080/tool/run \
	  -H 'Content-Type: application/json' \
	  -d '{"action":"docker_ps","args":{}}' | jq

test-tool:
	curl -s http://127.0.0.1:8080/tool/run \
	  -H 'Content-Type: application/json' \
	  -d '{"action":"shell_readonly","args":{"command":"ls -la","timeout":30}}' | jq

audit:
	curl -s http://127.0.0.1:8080/audit/events?limit=25 | jq

jobs:
	curl -s http://127.0.0.1:8080/jobs | jq

create-job:
	curl -s http://127.0.0.1:8080/jobs \
	  -H 'Content-Type: application/json' \
	  -d '{"instruction":"Inspect Docker runtime health.","schedule":"once","max_steps":6}' | jq

shell:
	docker exec -it agent-api sh

clean:
	docker compose down -v
