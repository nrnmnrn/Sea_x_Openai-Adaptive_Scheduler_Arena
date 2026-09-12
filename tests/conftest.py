import importlib

import pytest

from scheduler import create_backend


def pytest_addoption(parser):
    parser.addoption("--backend", choices=("local", "team"), default="local")
    parser.addoption("--factory", default=None)


@pytest.fixture(scope="session")
def backend_factory(request):
    backend_name = request.config.getoption("--backend")
    factory_path = request.config.getoption("--factory")
    if backend_name == "local":
        return create_backend
    if not factory_path or ":" not in factory_path:
        raise pytest.UsageError("team backend requires --factory module:function")
    module_name, function_name = factory_path.split(":", 1)
    try:
        module = importlib.import_module(module_name)
        factory = getattr(module, function_name)
    except (ImportError, AttributeError) as exc:
        raise pytest.UsageError(f"cannot load backend factory {factory_path}: {exc}") from exc
    if not callable(factory):
        raise pytest.UsageError(f"backend factory is not callable: {factory_path}")
    return factory
