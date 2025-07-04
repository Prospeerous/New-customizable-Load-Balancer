# Makefile for Load Balancer Project

.PHONY: help build run stop clean logs test-distribution test-scalability delete-server

help:
	@echo ""
	@echo "Available commands:"
	@echo "  make build              Build Docker containers"
	@echo "  make run                Run the full system with docker-compose"
	@echo "  make stop               Stop all containers"
	@echo "  make clean              Remove containers and networks"
	@echo "  make logs               View load balancer logs"
	@echo "  make test-distribution  Run test_distribution.py"
	@echo "  make test-scalability   Run test_scalability.py"
	@echo "  make delete-server      Run delete_and_monitor.py to simulate failure"
	@echo ""

build:
	docker compose build

run:
	docker compose up --build

stop:
	docker compose down

clean:
	docker compose down --remove-orphans
	docker network prune -f

logs:
	docker logs load_balancer

test-distribution:
	python analysis/test_distribution.py

test-scalability:
	python analysis/test_scalability.py

delete-server:
	python analysis/delete_and_monitor.py