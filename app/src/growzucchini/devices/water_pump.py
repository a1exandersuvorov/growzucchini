from growzucchini.config import config
from growzucchini.config.base import get_hardware_config
from growzucchini.core.registry import device_registry
from growzucchini.core.sensor_data import SensorData
from growzucchini.devices.duration_estimation_device import DurationEstimatingDevice
from growzucchini.devices.linear_device import LinearDevice

'''
T = ((M_target − M_current) / 100) × (V_pot / Q_pump)

Where:
  T         – pump run time (seconds)
  M_target  – target volumetric soil moisture (%)
  M_current – current volumetric soil moisture (%)
  V_pot     – total soil volume or effective wettable volume (liters)
  Q_pump    – pump flow rate (liters per second)
'''


@device_registry("water_pump")
class WaterPump(LinearDevice, DurationEstimatingDevice):
    async def estimate_runtime(self, sensor_data: SensorData) -> float:
        m_current = sensor_data.value
        m_target = config.growth_phase.SOIL_MOISTURE_CEIL
        v_pot = self.pot_volume
        q_pump = self.flow_rate

        delta_moisture = max(0.0, m_target - m_current)
        runtime = (delta_moisture / 100) * (v_pot / q_pump)
        return runtime

    @property
    def flow_rate(self):
        return get_hardware_config().get("WaterPump").FLOW_RATE

    @property
    def pot_volume(self):
        return get_hardware_config().get("WaterPump").POT_VOLUME
