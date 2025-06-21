import json

import pytest

from growzucchini.core.registry import Action
from growzucchini.core.sensor_data import Control
from growzucchini.devices.linear_device import LinearDevice


@pytest.fixture
def device():
    return LinearDevice()


@pytest.fixture
def control():
    return Control(1, "digital", "linear_device")


@pytest.mark.asyncio
async def test_linear_device_action_matches_current_state(ctx, device, control):
    # State same as action
    device.state = Action.UP.value

    await device(Action.UP, control, ctx.command_queue)

    assert ctx.command_queue.empty()


@pytest.mark.asyncio
async def test_linear_device_action_up(ctx, device, control):
    # State opposite action
    device.state = Action.DOWN.value

    await device(Action.UP, control, ctx.command_queue)

    assert not ctx.command_queue.empty()

    cmd_str = await ctx.command_queue.get()
    cmd = json.loads(cmd_str)
    # Command queue contains action
    assert cmd["value"] == Action.UP.value


@pytest.mark.asyncio
async def test_linear_device_action_down(ctx, device, control):
    # State opposite action
    device.state = Action.UP.value

    await device(Action.DOWN, control, ctx.command_queue)

    assert not ctx.command_queue.empty()

    cmd_str = await ctx.command_queue.get()
    cmd = json.loads(cmd_str)
    # Command queue contains action
    assert cmd["value"] == Action.DOWN.value
