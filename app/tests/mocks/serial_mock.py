import asyncio
from unittest.mock import MagicMock

class MockSerialConnectionManager:
    """
    Manages a mock serial connection for testing purposes.

    When `create_serial_connection` is called (typically patched in tests),
    it returns a mock transport and the actual protocol instance created by the
    application's protocol factory.

    The actual protocol instance is augmented with a `simulate_data_received` method,
    allowing tests to inject data as if it were coming from a serial device.
    """
    def __init__(self):
        self.mock_transport = None  # Stores the mock transport object
        self.protocol_instance = None  # Stores the actual protocol instance

    async def create_serial_connection(self, loop, protocol_factory, path, baudrate):
        """
        Mock version of serial_asyncio.create_serial_connection.

        Args:
            loop: The asyncio event loop.
            protocol_factory: A callable that returns an instance of the protocol
                              (e.g., the application's ArduinoProtocol).
            path (str): The serial port path (unused in mock).
            baudrate (int): The baud rate (unused in mock).

        Returns:
            A tuple (mock_transport, protocol_instance)
        """
        print(f"MockSerialConnectionManager: Mocking create_serial_connection for path={path}, baudrate={baudrate}")

        # Create a MagicMock for the transport object.
        # This mock_transport will be given to the protocol's connection_made method.
        # Application code can call mock_transport.write() and tests can assert those calls.
        self.mock_transport = MagicMock()

        # The protocol_factory is provided by the application code.
        # Calling it creates an instance of the actual protocol (e.g., ArduinoProtocol).
        self.protocol_instance = protocol_factory()

        # Call the protocol's connection_made method with the mock transport.
        # This mimics the behavior of the actual serial_asyncio.create_serial_connection.
        if hasattr(self.protocol_instance, 'connection_made') and callable(self.protocol_instance.connection_made):
            self.protocol_instance.connection_made(self.mock_transport)
        else:
            print("Warning: Protocol instance does not have a callable connection_made method.")


        # Dynamically add the simulate_data_received method to the protocol instance.
        # This allows test code to easily simulate data arriving from the serial port.
        def _simulate_data_received_on_protocol(data: str):
            """
            Simulates receiving data on the serial connection.
            This will call the protocol's data_received method with encoded data.
            """
            print(f"MockSerialConnectionManager: Simulating data received on protocol: '{data}'")
            if hasattr(self.protocol_instance, 'data_received') and callable(self.protocol_instance.data_received):
                self.protocol_instance.data_received(data.encode())
            else:
                # This case should ideally not happen if the protocol is standard.
                raise AttributeError(
                    f"Protocol instance {type(self.protocol_instance).__name__} "
                    "does not have a callable data_received method."
                )

        # Bind the simulation method to the protocol instance.
        # setattr(self.protocol_instance, 'simulate_data_received', _simulate_data_received_on_protocol)
        # Making it a direct method for easier use and discovery
        self.protocol_instance.simulate_data_received = _simulate_data_received_on_protocol

        print(f"MockSerialConnectionManager: Returning mock_transport and protocol_instance ({type(self.protocol_instance).__name__})")
        return (self.mock_transport, self.protocol_instance)

# Example usage in a test (illustrative):
#
# from app.tests.mocks.serial_mock import MockSerialConnectionManager
# from unittest.mock import patch
# import asyncio
#
# # Assume ArduinoProtocol is defined somewhere like app.core.comms.ArduinoProtocol
# # from app.core.comms import ArduinoProtocol
#
# # This would be your actual protocol
# class YourArduinoProtocol(asyncio.Protocol):
#     def __init__(self, command_queue):
#         self.queue = command_queue
#         self.transport = None
#         print("YourArduinoProtocol initialized")
#
#     def connection_made(self, transport):
#         self.transport = transport
#         print(f"YourArduinoProtocol: Connection made with {transport}")
#
#     def data_received(self, data):
#         decoded_data = data.decode().strip()
#         print(f"YourArduinoProtocol: Data received: {decoded_data}")
#         self.queue.put_nowait(decoded_data) # Example action
#
#     def connection_lost(self, exc):
#         print("YourArduinoProtocol: Connection lost")
#
# async def main_app_logic(loop, command_queue):
#     # In real app, serial_asyncio.create_serial_connection would be here
#     # For the test, it's patched.
#     # This is where you'd replace 'serial_asyncio' with the actual module path
#     # to create_serial_connection if it's different.
#     # For example, if it's `app.comms.create_serial_connection` use that path.
#     # Let's assume it's directly serial_asyncio for this example.
#     import serial_asyncio # Placeholder for where create_serial_connection is
#
#     # The factory creates the protocol instance
#     protocol_factory = lambda: YourArduinoProtocol(command_queue)
#
#     # Application calls the (now mocked) create_serial_connection
#     transport, protocol = await serial_asyncio.create_serial_connection(
#         loop, protocol_factory, '/dev/ttyACM0', 115200
#     )
#     # 'protocol' is now YourArduinoProtocol instance, augmented with simulate_data_received
#     # 'transport' is a MagicMock
#     return transport, protocol
#
# async def test_example():
#     mock_serial_manager = MockSerialConnectionManager()
#     command_queue = asyncio.Queue()
#
#     # Patch the actual create_serial_connection used by your application
#     # The path 'serial_asyncio.create_serial_connection' must match where your app code calls it.
#     # If your app has `from serial_module import create_serial_connection`, then patch `serial_module.create_serial_connection`.
#     with patch('serial_asyncio.create_serial_connection', new=mock_serial_manager.create_serial_connection):
#         # Run the part of your application that sets up the serial connection
#         # This will call mock_serial_manager.create_serial_connection
#         app_transport, app_protocol = await main_app_logic(asyncio.get_event_loop(), command_queue)
#
#     # Now, mock_serial_manager holds references to the transport and protocol
#     assert mock_serial_manager.mock_transport is app_transport
#     assert mock_serial_manager.protocol_instance is app_protocol
#     assert hasattr(app_protocol, 'simulate_data_received')
#
#     print("Test: Simulating data from Arduino...")
#     app_protocol.simulate_data_received("HELLO_FROM_ARDUINO\r\n")
#
#     # Check if data was received and processed by YourArduinoProtocol
#     received_item = await command_queue.get()
#     assert received_item == "HELLO_FROM_ARDUINO"
#     print(f"Test: Verified data on queue: {received_item}")
#
#     # Example: Test sending data via transport
#     print("Test: Simulating sending data to Arduino...")
#     app_transport.write(b"PING_TO_ARDUINO\r\n")
#     mock_serial_manager.mock_transport.write.assert_called_with(b"PING_TO_ARDUINO\r\n")
#     print("Test: Verified transport.write was called.")
#
# if __name__ == '__main__':
#     # To run the example test:
#     # 1. Make sure you have a `serial_asyncio` module or a placeholder for patching.
#     #    For a real scenario, this would be the actual library.
#     #    For this example, we can create a dummy serial_asyncio.py if needed or ensure the test runs
#     #    in an environment where it can be mocked (e.g. by creating a dummy module in sys.modules).
#
#     # Quick way to make `serial_asyncio` patchable for the example:
#     class DummySerialAsyncio:
#         async def create_serial_connection(self, loop, protocol_factory, path, baudrate):
#             # This is the real function that would be patched
#             raise NotImplementedError("This should be patched by the mock")
#
#     import sys
#     sys.modules['serial_asyncio'] = DummySerialAsyncio()
#
#     asyncio.run(test_example())
#
# print("app/tests/mocks/serial_mock.py defined with MockSerialConnectionManager.")
