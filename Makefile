PROTOCOL_VERSION?=v0.10.0

clean:
	rm saturn_bot/protocol/v1/saturnbot.proto
	rm saturn_bot/plugin/grpc_controller.proto

generate: saturn_bot/protocol/v1/saturnbot.proto saturn_bot/plugin/grpc_controller.proto
	buf generate
	touch saturn_bot/protocol/__init__.py
	touch saturn_bot/protocol/v1/__init__.py
	touch saturn_bot/plugin/__init__.py
	docker run -it --rm -v ${PWD}:/github/workspace ghcr.io/apache/skywalking-eyes/license-eye header fix

saturn_bot/protocol/v1/saturnbot.proto:
	mkdir -p ./saturn_bot/protocol/v1/
	curl -L -o ./saturn_bot/protocol/v1/saturnbot.proto --silent --fail https://raw.githubusercontent.com/wndhydrnt/saturn-bot-protocol/$(PROTOCOL_VERSION)/protocol/v1/saturnbot.proto

saturn_bot/plugin/grpc_controller.proto:
	mkdir -p ./plugin/
	curl -L -o ./saturn_bot/plugin/grpc_controller.proto --silent --fail https://raw.githubusercontent.com/hashicorp/go-plugin/v1.6.0/internal/plugin/grpc_controller.proto

lint:
	poetry run black --check .
	poetry run mypy .
	poetry run isort --check-only .
	poetry run flake8

test:
	poetry run pytest .

test_coverage:
	rm .coverage || true
	rm -rf ./htmlcov/
	poetry run coverage run
	poetry run coverage html
