import asyncio
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_command_queue():
    """
    Provides a mock asyncio.Queue for testing command processing.
    This can be used when instantiating protocols or other components
    that rely on a queue for inter-task communication.
    """
    queue = asyncio.Queue()
    # You could also use a MagicMock if you don't need full queue behavior
    # but rather just want to assert calls like put_nowait.
    # For example:
    # mock_queue = MagicMock(spec=asyncio.Queue)
    # return mock_queue
    return queue

@pytest.fixture
def mock_serial_connection_manager():
    """
    Provides an instance of the MockSerialConnectionManager.
    This fixture can be used to patch the actual serial connection creation
    in tests.
    """
    # Ensure the mock module is importable.
    # This might require adjusting sys.path or ensuring your test runner handles it.
    # For now, assuming it's directly importable if tests are run from the root
    # or if app is installed in editable mode.
    from app.tests.mocks.serial_mock import MockSerialConnectionManager
    return MockSerialConnectionManager()

# Example of how a test might use these fixtures:
#
# from unittest.mock import patch
#
# async def test_with_mock_queue_and_serial(mock_command_queue, mock_serial_connection_manager):
#     # Patch the location where create_serial_connection is called in your application code
#     # e.g., 'app.core.comms.create_serial_connection'
#     with patch('your_application_module.serial_asyncio.create_serial_connection',
#                new=mock_serial_connection_manager.create_serial_connection):
#
#         # ... initialize your application component that uses the serial connection ...
#         # This component should be configured to use mock_command_queue
#
#         # Simulate data coming from serial
#         assert mock_serial_connection_manager.protocol_instance is not None
#         mock_serial_connection_manager.protocol_instance.simulate_data_received("TEST_DATA\r\n")
#
#         # Assert that data was processed and put onto the queue
#         processed_data = await asyncio.wait_for(mock_command_queue.get(), timeout=1)
#         assert processed_data == "TEST_DATA"
#
#         # Assert that something was written to serial
#         mock_serial_connection_manager.mock_transport.write.assert_called_with(b"RESPONSE\r\n")

print("app/tests/conftest.py created/updated with mock_command_queue fixture.")
