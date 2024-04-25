PROTOCOL_VERSION?=v0.7.0

clean:
	rm saturn_sync/protocol/v1/saturnsync.proto
	rm saturn_sync/plugin/grpc_controller.proto

generate: saturn_sync/protocol/v1/saturnsync.proto saturn_sync/plugin/grpc_controller.proto
	buf generate
	touch saturn_sync/protocol/__init__.py
	touch saturn_sync/protocol/v1/__init__.py
	touch saturn_sync/plugin/__init__.py
	docker run -it --rm -v ${PWD}:/github/workspace ghcr.io/apache/skywalking-eyes/license-eye header fix

saturn_sync/protocol/v1/saturnsync.proto:
	mkdir -p ./saturn_sync/protocol/v1/
	curl -L -o ./saturn_sync/protocol/v1/saturnsync.proto --silent --fail https://raw.githubusercontent.com/wndhydrnt/saturn-sync-protocol/$(PROTOCOL_VERSION)/protocol/v1/saturnsync.proto

saturn_sync/plugin/grpc_controller.proto:
	mkdir -p ./plugin/
	curl -L -o ./saturn_sync/plugin/grpc_controller.proto --silent --fail https://raw.githubusercontent.com/hashicorp/go-plugin/v1.6.0/internal/plugin/grpc_controller.proto

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
