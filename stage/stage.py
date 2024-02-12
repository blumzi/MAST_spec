import zaber_motion.ascii
import utils
from utils import Component, Activities, init_log
import logging
from enum import Flag, auto, Enum
from utils import Config, PrettyJSONResponse
from fastapi import APIRouter

cfg = Config()
logger = logging.getLogger('mast.spec.stage')
init_log(logger)

stage_names = list(cfg.toml['stages'].keys())
stage_names.remove('controller')


def on_error(arg):
    logger.error(f"on_error: {arg}")


def on_completion(e: zaber_motion.ascii.AlertEvent):
    for s in stages:
        if stages[s].axis_id == e.axis_number:
            stages[s].on_event(e)
            return


def on_next(e: zaber_motion.ascii.AlertEvent):
    for s in stages:
        if stages[s].axis_id == e.axis_number:
            stages[s].on_event(e)
            return


def connect() -> zaber_motion.ascii.Device:
    dev: zaber_motion.ascii.Device

    ipaddr = cfg.toml['stages']['controller']['ipaddr']
    port = cfg.toml['stages']['controller']['port']
    if ipaddr is None:
        raise f"Cannot get configuration entry [stages.controller].ipaddr"
    conn = zaber_motion.ascii.Connection.open_tcp(host_name=ipaddr, port=port)
    conn.enable_alerts()
    conn.alert.subscribe(on_error=on_error, on_completed=on_completion, on_next=on_next)
    dev = conn.get_device(1)
    dev.identify()

    return dev


controller: zaber_motion.ascii.Device | None = None

if controller is None:
    controller = connect()


class StageActivities(Flag):
    Homing = auto()
    Moving = auto()
    Parking = auto()
    StartingUp = auto()
    ShuttingDown = auto()
    Aborting = auto()


class StageStatus:
    activities: Flag
    position: float

    def __init__(self, activities: Flag, position: float):
        self.activities = activities
        self.position = position


class Stage(Component, Activities):
    name: str
    axis: zaber_motion.ascii.Axis | None
    logger: logging.Logger
    target: float | None = None
    target_units: zaber_motion.Units
    presets_microns: dict

    def __init__(self, stage_name: str):
        super().__init__()

        if stage_name not in stage_names:
            raise f"Bad stage name '{stage_name}'.  Known names are: {stage_names}"

        self.name = stage_name
        self.logger = logging.getLogger(f"mast.spec.stage.{self.name}")
        init_log(self.logger)

        self.axis_id = cfg.toml['stages']['controller'][self.name]
        if self.axis_id is None:
            raise f"Missing configuration item '[stages.controller].{self.name}"

        self.presets_microns = dict()
        for key in cfg.toml['stages'][self.name]['presets'].keys():
            self.presets_microns[key] = cfg.toml['stages'][self.name]['presets'][key]

        try:
            self.axis = controller.get_axis(self.axis_id)
            if self.axis.axis_type == zaber_motion.ascii.AxisType.UNKNOWN:
                self.logger.info(f"No stage '{self.name}' (index={self.axis_id})")
                self.axis = None
                return
            t = str(self.axis.axis_type).replace('AxisType.', '')
            self.logger.info(f"Found stage name='{self.name}', type={t},"
                             f"peripheral='{self.axis.identity.peripheral_name}'")

            if self.axis.is_parked():
                self.axis.unpark()
            elif not self.axis.is_homed():
                self.start_activity(StageActivities.Homing)
                self.axis.home()

        except Exception as ex:
            self.logger.critical(f"Could not get a Zaber controller handle to unit")

    def on_event(self, e: zaber_motion.ascii.AlertEvent):
        if e.status == 'IDLE':
            if self.is_active(StageActivities.Parking):
                self.end_activity(StageActivities.Parking)
            if self.is_active(StageActivities.ShuttingDown):
                self.end_activity(StageActivities.ShuttingDown)
            if self.is_active(StageActivities.Aborting):
                self.end_activity(StageActivities.Aborting)
            if self.is_active(StageActivities.Homing):
                self.end_activity(StageActivities.Homing)
            if self.is_active(StageActivities.Moving):
                self.end_activity(StageActivities.Moving)
                self.target = None
        else:
            self.logger.error(f"Got unknown event: {e}")

    def move_relative(self, amount: float, unit: zaber_motion.Units):
        if self.axis is None:
            return
        self.start_activity(StageActivities.Moving)
        self.axis.move_relative(amount, unit=unit)

    def move_absolute(self, position: float, unit: zaber_motion.Units):
        if self.axis is None:
            return
        self.start_activity(StageActivities.Moving)
        self.axis.move_absolute(position, unit=unit)

    def move_to_preset(self, preset: str):
        if self.axis is None:
            return
        if preset not in self.presets_microns:
            raise ValueError(f"Bad preset '{preset}. Valid presets are; {",".join(self.presets_microns.keys())}")

        self.target = self.presets_microns[preset]
        self.target_units = zaber_motion.Units.LENGTH_MICROMETRES
        self.start_activity(StageActivities.Moving)
        self.axis.move_absolute(self.target, self.target_units)

    def shutdown(self):
        if self.axis is None:
            return
        self.start_activity(StageActivities.ShuttingDown)
        self.start_activity(StageActivities.Parking)
        self.axis.park()

    def startup(self):
        if self.axis is None:
            return
        self.start_activity(StageActivities.StartingUp)
        if self.axis.is_parked():
            self.axis.unpark()
        elif not self.axis.is_homed():
            self.start_activity(StageActivities.Homing)
            self.axis.home(wait_until_idle=False)

    def abort(self):
        if self.axis is None:
            return
        self.start_activity(StageActivities.Aborting)
        self.axis.stop(wait_until_idle=False)

    @property
    def position(self) -> float | None:
        if self.axis is None:
            return float('nan')
        return self.axis.get_position()

    def status(self) -> StageStatus:
        return StageStatus(self.activities, self.position)


stages = {}
stages_dict = {}
for name in stage_names:
    stages[name] = Stage(name)
    stages_dict[name] = name

StageNames = Enum('StageNames', stages_dict)

units_dict = {}
reverse_units_dict = {}
for u in zaber_motion.Units:
    if u.name.startswith('LENGTH_') or u.name == 'NATIVE':
        v = u.name.replace('LENGTH_', '')
        units_dict[v] = v
        reverse_units_dict[v] = u
UnitNames = Enum('UnitNames', units_dict)


# FastApi stuff
def list_stages():
    response = {}
    for s in stages:
        response[s] = f"{stages[s].axis}"
    return response


def get_position(stage: StageNames):
    s = stage.value
    if s in stage_names and stages[s].axis is not None:
        return stages[s].position
    else:
        return {
            'Error': f"No physical stage for '{s}'"
        }


def get_status(stage: StageNames):
    s = stage.value
    if s in stage_names and stages[s].axis is not None:
        return stages[s].status()
    else:
        return {
            'Error': f"No physical stage for '{s}'"
        }


def move_absolute(stage: StageNames, position: float, units: UnitNames):
    s = stage.value
    if s in stage_names and stages[s].axis is not None:
        stages[s].move_absolute(position, reverse_units_dict[units.value])
    else:
        return {
            'Error': f"No physical stage for '{s}'"
        }


def move_relative(stage: StageNames, position: float, units: UnitNames):
    s = stage.value
    if s in stage_names and stages[s].axis is not None:
        stages[s].move_absolute(position, reverse_units_dict[units.value])
    else:
        return {
            'Error': f"No physical stage for '{s}'"
        }


PresetNames = Enum('PresetNames', {
    'Ca': 'Ca',
    'Mg': 'Mg',
    'Halpha': 'Halpha',
    'DeepSpec': 'DeepSpec',
    'HighSpec': 'HighSpec'
})


def move_to_preset(stage: StageNames, preset: PresetNames):
    s = stage.value
    if s in stage_names and stages[s].axis is not None:
        if (preset.value == 'HighSpec' or preset.value == 'DeepSpec') and s != 'fiber':
            return {
                'Error': f"Only the 'fiber' stage has presets named 'DeepSpec' or 'HighSpec'"
            }
        if (preset.value == 'Ca' or preset.value == 'Mg' or preset.value == 'Halpha') and s == 'fiber':
            return {
                'Error': f"The 'fiber' stage has presets named 'DeepSpec' or 'HighSpec'"
            }

        stages[s].move_to_preset(preset.value)
    else:
        return {
            'Error': f"No physical stage for '{s}'"
        }


base_path = utils.BASE_SPEC_PATH + 'stages'
tag = 'stages'
router = APIRouter()

router.add_api_route(base_path, tags=[tag], endpoint=list_stages, response_class=PrettyJSONResponse)
router.add_api_route(base_path + '/position', tags=[tag], endpoint=get_position, response_class=PrettyJSONResponse)
router.add_api_route(base_path + '/status', tags=[tag], endpoint=get_status, response_class=PrettyJSONResponse)
router.add_api_route(base_path + '/move_absolute', tags=[tag], endpoint=move_absolute,
                     response_class=PrettyJSONResponse)
router.add_api_route(base_path + '/move_relative', tags=[tag], endpoint=move_relative,
                     response_class=PrettyJSONResponse)
router.add_api_route(base_path + '/move_to_preset', tags=[tag], endpoint=move_to_preset,
                     response_class=PrettyJSONResponse)
