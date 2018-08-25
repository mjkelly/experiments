.PHONY: clean run

build:
	docker build -t nodetest:latest .

run: build
	docker run -t -i -p 8080:8080 nodetest:latest

local-build:
	npm install

local-run:
	nodejs ./server.js
