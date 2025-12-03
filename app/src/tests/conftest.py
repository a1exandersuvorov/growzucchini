import pytest
import asyncio

from unittest.mock import AsyncMock, MagicMock

from katomato.core.registry import DEVICE_REGISTRY


@pytest.fixture(name="ctx")
def controller_test_context():
    class ControllerTestContext:
        def __init__(self):
            self.command_queue = asyncio.Queue()
            self.mock_device = AsyncMock()
            self.mock_ctrl = MagicMock()
            self.mock_ctrl.device = "device"
            DEVICE_REGISTRY["device"] = self.mock_device

    return ControllerTestContext()
