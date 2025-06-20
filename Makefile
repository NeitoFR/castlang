.PHONY: up down kill restart

up:
	docker compose up -d

down:
	docker compose down

kill:
	docker compose kill

restart:
	docker compose restart
