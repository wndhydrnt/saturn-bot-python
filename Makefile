PROTOCOL_VERSION?=v0.11.1
INTEGRATION_TEST_BIN=integration-test-$(PROTOCOL_VERSION).$(shell uname -s)-$(shell uname -m)
INTEGRATION_TEST_PATH=integration_test/$(INTEGRATION_TEST_BIN)

clean:
	rm saturn_bot/protocol/v1/saturnbot.proto
	rm saturn_bot/plugin/grpc_controller.proto
	rm saturn_bot/plugin/grpc_stdio.proto

generate: saturn_bot/protocol/v1/saturnbot.proto saturn_bot/plugin/grpc_controller.proto saturn_bot/plugin/grpc_stdio.proto
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

saturn_bot/plugin/grpc_stdio.proto:
	mkdir -p ./plugin/
	curl -L -o ./saturn_bot/plugin/grpc_stdio.proto --silent --fail https://raw.githubusercontent.com/hashicorp/go-plugin/v1.6.0/internal/plugin/grpc_stdio.proto

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

$(INTEGRATION_TEST_PATH):
	curl -fsSL -o $(INTEGRATION_TEST_PATH) "https://github.com/wndhydrnt/saturn-bot-protocol/releases/download/$(PROTOCOL_VERSION)/$(INTEGRATION_TEST_BIN)"
	chmod +x $(INTEGRATION_TEST_PATH)

test_integration: $(INTEGRATION_TEST_PATH)
	$(INTEGRATION_TEST_PATH) -path integration_test/plugin.py
