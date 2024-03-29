from utils import Component, Activities, RepeatTimer, init_log, PrettyJSONResponse, BASE_SPEC_PATH
from enum import IntFlag, Enum, auto
import logging
from fastapi import APIRouter
from typing import List
from config.config import Config
from dlipower.dlipower.dlipower import SwitchedPowerDevice

import sys
import os.path
sys.path.append(os.path.dirname(__file__))
from sdk.FWxC_COMMAND_LIB import *


class SpeedMode(int, Enum):
    Slow = 0,
    High = 1,


class SensorMode(int, Enum):
    Off = 0,
    On = 1,


class WheelActivities(IntFlag):
    StartingUp = auto()
    ShuttingDown = auto()
    Moving = auto()


class Wheel(Component, SwitchedPowerDevice, Activities):
    serial_number: str
    device: int | None
    name: str
    positions: dict
    default_position: int | None
    target: int | None = None
    timer: RepeatTimer
    switch_logger = None
    sensor_mode: SensorMode
    speed_mode: SpeedMode
    positions: int

    def __init__(self, wheel_name: str):
        Activities.__init__(self)

        self.name = wheel_name

        self.logger = logging.getLogger(f"mast.spec.filter-wheel-{self.name}")
        init_log(self.logger)

        self.conf = Config().toml['filter-wheel'][self.name]
        SwitchedPowerDevice.__init__(self, self.conf)
        self.serial_number = self.conf['serial_number']
        self.positions = dict()
        for k, v in self.conf.items():
            if k == 'serial_number' or k == 'default':
                continue
            self.positions[k] = v

        prefix = f"'{self.name} (sn: {self.serial_number})'"

        devices = FWxCListDevices()
        found = [dev for dev in devices if dev[0] == self.serial_number]
        if len(found) == 0:
            self.device = None
            self.logger.error(f"{prefix}: Could not find device")
            return

        self.device = FWxCOpen(self.serial_number, 115200, 3)
        if self.device < 0:
            self.logger.error(f"{prefix}: Could not open device")
            self.device = None
            return

        _id = []
        result = FWxCGetId(self.device, _id)
        if result < 0:
            self.logger.error(f"{prefix}: Could not get id")
            self.device = None
            return
        _id[0] = _id[0][6:]
        self.id: str = _id[0][:-3]

        npos = [self.device]
        result = FWxCGetPositionCount(self.device, npos)
        if result < 0:
            self.logger.error(f"{prefix}: Could not get number of positions")
            self.device = None
            return

        expected_number_of_positions = 6
        if npos[0] != expected_number_of_positions:
            self.logger.error(f"{prefix} expected {expected_number_of_positions} positions, got {npos[0]}")
            self.device = None
            return

        self.positions = npos[0]
        self.logger.info(f"{prefix}: positions={self.positions}, id='{self.id}'")

        # set the speed mode to 'high' (1)
        result = FWxCSetSpeedMode(self.device, SpeedMode.High.value)
        if result < 0:
            self.logger.error(f"{prefix}: Could not set speed mode to {SpeedMode.High.value}")
            self.device = None
            return

        mode = [SpeedMode.High.value]
        result = FWxCGetSpeedMode(self.device, mode)
        if result < 0:
            self.logger.error(f"{prefix}: Could not get speed mode")
            self.device = None
            return
        if mode[0] != SpeedMode.High.value:
            self.logger.error(f"{prefix}: Failed to set speed mode to {SpeedMode.High}")
            self.device = None
            return

        self.speed_mode = SpeedMode.High
        self.logger.info(f"{prefix}: Speed mode was set to {SpeedMode.High}")

        # set the sensor mode to 'OFF' (normally OFF, ON only when wheel rotates)
        mode = [0]
        result = FWxCGetSensorMode(self.device, mode)
        if result < 0:
            self.logger.error(f"{prefix}: Could not get sensor mode")
            self.device = None
            return
        if mode[0] == SensorMode.Off.value:
            self.logger.info(f"{prefix}: Sensor mode is {SensorMode.Off}")
        else:
            mode[0] = SensorMode.Off.value
            result = FWxCSetSensorMode(self.device, mode)
            if result < 0:
                self.logger.error(f"{prefix}: Could not set sensor mode to {SensorMode.Off}")
                self.device = None
                return
            result = FWxCGetSensorMode(self.device, mode)
            if result < 0:
                self.logger.error(f"{prefix}: Could not get sensor mode")
                self.device = None
                return
            if mode[0] != SensorMode.Off.value:
                self.logger.error(f"{prefix}: Could not set sensor mode to {SensorMode.Off}")
                self.device = None
                return
            else:
                self.logger.info(f"{prefix}: Sensor mode was set to {SensorMode.Off}")
        self.sensor_mode = SensorMode.Off

        result = FWxCSave(self.device)
        if result < 0:
            self.logger.error(f"Could not save")
            self.device = None
            return
        self.logger.info(f"{prefix}: Saved")

        self.positions = dict()
        for i in range(1, 7):
            self.positions[i] = self.conf[str(i)]
        if 'default' in self.conf:
            self.default_position = self.conf["default"]
        else:
            self.default_position = None

        self.timer = RepeatTimer(1, function=self.ontimer)
        self.timer.name = f'{self.name}-timer-thread'
        self.timer.start()

        self.logger.info('initialized')

    def __del__(self):
        if self.device is not None:
            FWxCClose(self.device)

    def startup(self):
        """
        Go to default position
        :return:
        """
        if self.device is None:
            return

        if (hasattr(self, 'default_position') and self.default_position is not None and
                self.position != self.default_position):
            self.start_activity(WheelActivities.StartingUp)
            self.move(self.default_position)

    def shutdown(self):
        """
        Return to default position
        :return:
        """
        if self.device is None:
            return

        if self.default_position is not None and self.position != self.default_position:
            self.start_activity(WheelActivities.ShuttingDown)
            self.move(self.default_position)

    def abort(self):
        # The wheel cannot be stopped
        if self.is_active(WheelActivities.Moving):
            self.end_activity(WheelActivities.Moving)

    def status(self) -> dict:
        return {
            'serial_number': self.serial_number,
            'id': self.id,
            'position': self.position,
            'speed_mode': self.speed_mode,
            'sensor_mode': self.sensor_mode,
        }

    @property
    def position(self) -> int | None:
        """
        Get the current position from the controller
        :return:
        """
        pos = [0]
        result = FWxCGetPosition(self.device, pos)
        if result < 0:
            self.logger.error(f"'{self.serial_number}: Could not get position")
            return None
        return pos[0]

    def move(self, pos: str | int):
        if isinstance(pos, str):
            try:
                pos = int(pos)
            except ValueError:
                for k, v in self.positions.items():
                    if pos == v:
                        pos = int(k)
                        break

        if pos == self.position:
            self.logger.debug(f"Already at position {pos} ('{self.positions[pos]}')")
            return

        if pos in range(len(self.positions.keys()) + 1):
            self.target = pos
            self.start_activity(WheelActivities.Moving)
            self.logger.debug(f"Moving to position {pos} ('{self.positions[pos]}')")
            FWxCSetPosition(self.device, self.target)
        else:
            return {'Error': f"Valid positions on the '{self.name}' wheel: {self.positions}"}

    def name_to_number(self, pos_name: str) -> int | None:

        for k, v in self.positions.items():
            if v == pos_name:
                return k

        raise Exception(f"Bad position name '{pos_name}'.  Known position names: {self.positions}")

    def ontimer(self):
        if self.is_active(WheelActivities.Moving) and self.position == self.target:
            self.end_activity(WheelActivities.Moving)
            self.target = None

            if self.is_active(WheelActivities.StartingUp):
                self.end_activity(WheelActivities.StartingUp)
            if self.is_active(WheelActivities.ShuttingDown):
                self.end_activity(WheelActivities.ShuttingDown)

    def __repr__(self):
        return f"<Wheel-{self.id}>(name='{self.name}', serial='{self.serial_number}')"


def make_filter_wheels():
    cfg = Config()

    ret: List[Wheel] = list()
    for wheel_name in cfg.toml['filter-wheel']:
        ret.append(Wheel(wheel_name))
    return ret


wheels = make_filter_wheels()


def list_wheels():
    ret = {}
    for wheel in wheels:
        d = {
            'serial_number': wheel.serial_number,
        }
        if wheel.device is not None:
            d['device'] = wheel.id
            d['positions'] = {}
            for k, v in wheel.positions:
                d['positions'][k] = v
        else:
            d['device'] = 'not-detected'
        ret[wheel.name] = d
    return ret


class WheelNames(str, Enum):
    ThAr = "ThAr"
    qTh = "qTh"


def wheel_by_name(name: WheelNames) -> Wheel | None:
    for w in wheels:
        if w.name == name.value:
            return w
    return None


def get_position(wheel: WheelNames):
    w = wheel_by_name(wheel)
    if w is not None:
        if w.device is None:
            return {'Error': f'{w.serial_number}: device not detected'}
        return w.position


def get_status(wheel: WheelNames):
    w = wheel_by_name(wheel)
    if w is not None:
        if w.device is None:
            return {'Error': f'{w.serial_number}: device not detected'}
        return w.status()


def move(wheel: WheelNames, position: int | str):
    w = wheel_by_name(wheel)
    if w is not None:
        if w.device is None:
            return {'Error': f'{w.serial_number}: device not detected'}
        if isinstance(position, str):
            for n, v in w.positions.items():
                if v == position:
                    position = n
                    break
        return w.move(position)


def startup():
    for w in wheels:
        w.startup()


def shutdown():
    for w in wheels:
        w.shutdown()


def abort():
    for w in wheels:
        w.abort()


base_path = BASE_SPEC_PATH + 'fw'
tag = 'filter-wheel'
router = APIRouter()

router.add_api_route(base_path, tags=[tag], endpoint=list_wheels, response_class=PrettyJSONResponse)
router.add_api_route(base_path + '/position', tags=[tag], endpoint=get_position, response_class=PrettyJSONResponse)
router.add_api_route(base_path + '/status', tags=[tag], endpoint=get_status, response_class=PrettyJSONResponse)
router.add_api_route(base_path + '/move', tags=[tag], endpoint=move,
                     response_class=PrettyJSONResponse)

router.add_api_route(base_path + '/startup', tags=[tag], endpoint=startup, response_class=PrettyJSONResponse)
router.add_api_route(base_path + '/shutdown', tags=[tag], endpoint=shutdown, response_class=PrettyJSONResponse)
router.add_api_route(base_path + '/abort', tags=[tag], endpoint=abort, response_class=PrettyJSONResponse)

if __name__ == '__main__':
    wheels[0].move(5)