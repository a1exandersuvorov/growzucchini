import pytest
import asyncio

from unittest.mock import AsyncMock, MagicMock

from growzucchini.core.registry import DEVICE_REGISTRY


@pytest.fixture(name="ctx")
def controller_test_context():
    class ControllerTestContext:
        def __init__(self):
            self.command_queue = asyncio.Queue()
            self.device_mock = AsyncMock()
            self.ctrl = MagicMock()
            self.ctrl.device = "device"
            DEVICE_REGISTRY["device"] = self.device_mock

    return ControllerTestContext()
