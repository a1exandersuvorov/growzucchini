import json
from unittest.mock import MagicMock

import pytest

from katosup.core.registry import Action
from katosup.core.sensor_data import Control, State
from katosup.devices.exhaust_fan import ExhaustFan


@pytest.fixture
def device():
    return ExhaustFan()


@pytest.fixture
def control():
    return Control(pin=1, type="pwm", device="exhaust_fan")


@pytest.mark.asyncio
async def test_exhaust_fan_threshold_detection(ctx, device, control, monkeypatch):
    monkeypatch.setattr(
        "katosup.devices.exhaust_fan.get_hardware_config",
        lambda: {"ExhaustFan": MagicMock(FAN_SPEED_FLOOR=100)}
    )

    # Simulate gradually increasing RPM values until threshold is reached
    for idx, pwm in enumerate(device.pwm_values):
        state = State(value=50 + idx * 10)
        await device(state, control, ctx.command_queue)
        if state.value >= 100:
            assert device.rpm_threshold_determined
            assert device.rpm_threshold_idx == idx
            break

    assert not ctx.command_queue.empty()


@pytest.mark.asyncio
async def test_exhaust_fan_action_up_when_exceed_threshold(ctx, device, control):
    # Pre-mark the threshold as determined
    device.rpm_threshold_determined = True
    device.current_rpm_idx = 5
    device.rpm_threshold_idx = 3

    await device(Action.UP, control, ctx.command_queue)
    assert device.current_rpm_idx == 4

    assert not ctx.command_queue.empty()
    cmd_str = await ctx.command_queue.get()
    cmd = json.loads(cmd_str)
    assert cmd["value"] == device.pwm_values[device.current_rpm_idx]

    await device(Action.DOWN, control, ctx.command_queue)
    assert device.current_rpm_idx == 5

    await device(Action.DOWN, control, ctx.command_queue)
    assert device.current_rpm_idx == 6


@pytest.mark.asyncio
async def test_exhaust_fan_action_up_when_idx_equals_threshold(ctx, device, control):
    device.rpm_threshold_determined = True
    device.current_rpm_idx = 3
    device.rpm_threshold_idx = 3

    await device(Action.UP, control, ctx.command_queue)

    assert ctx.command_queue.empty()
    assert device.current_rpm_idx == 3


@pytest.mark.asyncio
async def test_exhaust_fan_action_down_when_in_pwm_range(ctx, device, control):
    device.rpm_threshold_determined = True
    device.current_rpm_idx = 4

    await device(Action.DOWN, control, ctx.command_queue)
    assert device.current_rpm_idx == 5

    assert not ctx.command_queue.empty()
    cmd_str = await ctx.command_queue.get()
    cmd = json.loads(cmd_str)
    assert cmd["value"] == device.pwm_values[device.current_rpm_idx]


@pytest.mark.asyncio
async def test_exhaust_fan_action_down_when_out_range(ctx, device, control):
    device.rpm_threshold_determined = True
    device.current_rpm_idx = 11

    await device(Action.DOWN, control, ctx.command_queue)

    assert ctx.command_queue.empty()
    assert device.current_rpm_idx == 11
