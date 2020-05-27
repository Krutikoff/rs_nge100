
import pyvisa
import time
import json
import re
from pyvisa import Resource
from enum import Enum, IntEnum
from typing import Tuple, Union, Optional, Dict


class CmdTypes(IntEnum):
    SET_VOLTAGE_AND_CURRENT = 0,
    SET_VOLTAGE = 1,
    SET_CURRENT = 2,
    GET_VOLTAGE_AND_CURRENT = 3
    GET_VOLTAGE = 4,
    GET_CURRENT = 5
    SET_SUPPLY = 6
    DISABLE_SUPPLY = 7

class Chanels(Enum):
    CH1 = "Chanel_1"
    CH2 = "Chanel_2"
    CH3 = "Chanel_3"

class ParamTypes(Enum):
    CHANEL_ID = "Id"
    VOLTAGE = "Voltage"
    CURRENT = "Current"
    OUTPUT_STATE = "OutputState"

class SupplyStates(Enum):
    ENABLE = "ON"
    DISABLE = "OFF"

class SetParamCmd:
    chanel: int
    voltage: int
    current: int

class SetSupplyCmd:
    chanel: int
    state: SupplyStates


class RsNge100():
    _USB_CONFIG = "config/usb.json"
    _CONFIG = "config/rs_nge100.json"

    def __init__(self):
        self._cmd_templates = {
            CmdTypes.SET_VOLTAGE_AND_CURRENT: 'INST OUT{chanel}; APPLY "{vol}, {cur}"',
            CmdTypes.SET_VOLTAGE: 'INST OUT{chanel}; APPLY "{voltage},2"',
            CmdTypes.SET_CURRENT: 'INST OUT{chanel}; APPLY "6,{cur}"',
            CmdTypes.GET_VOLTAGE_AND_CURRENT: 'INST OUT{chanel}; APPLY?',
            CmdTypes.SET_SUPPLY: 'INST OUT{chanel}; OUTP {state}; OUTP:GEN {state}',
        }
        self._rm = pyvisa.ResourceManager()
        self._instr = self._init_instrument()
        self._config = self._init_params()


    def set_parameter(self, chanel: Chanels, param: ParamTypes, value: Union[int, float] ) -> None:
        self._config[chanel.value][param.value] = value

        cmd = SetParamCmd()
        cmd.chanel = self._config[chanel.value][ParamTypes.CHANEL_ID.value]
        cmd.voltage = self._config[chanel.value][ParamTypes.VOLTAGE.value]
        cmd.current = self._config[chanel.value][ParamTypes.CURRENT.value]

        packet = self._build(cmd)
        self._instr.write(packet)
        self._save_config()

    def set_supply(self, chanel: Chanels, state: SupplyStates):
        cmd = SetSupplyCmd()
        cmd.chanel = self._config[chanel.value][ParamTypes.CHANEL_ID.value]
        cmd.state = state.value

        packet = self._build(cmd)
        self._instr.write(packet)
        self._save_config()

    def _build(self, cmd: Union[SetParamCmd, SetSupplyCmd]) -> Optional[str]:
        temp: Optional[str] = None
        packet: Optional[str] = None
        
        if isinstance(cmd, SetParamCmd):
            temp = self._cmd_templates[CmdTypes.SET_VOLTAGE_AND_CURRENT]
            chanel = cmd.chanel
            voltage = cmd.voltage
            current = cmd.current
            packet = temp.format(chanel =chanel, vol = voltage, cur = current)
        elif isinstance(cmd, SetSupplyCmd):
            temp = self._cmd_templates[CmdTypes.SET_SUPPLY]
            chanel = cmd.chanel
            state = cmd.state
            packet = temp.format(chanel =chanel, state = state)

        return packet


    def _init_instrument(self) -> Resource:
        name = self._init_resource_name()
        return self._rm.open_resource(name)


    def _init_resource_name(self) -> Optional[str]:
        usb_config = self._extract_data_from_file(RsNge100._USB_CONFIG)
        vid = usb_config["VID"]
        pid = usb_config["PID"]

        names = self._rm.list_resources()
        for name in names:
            if vid in name and pid in name:
                return name

        # Change to Exception
        return None

    def _init_params(self):
        return self._extract_data_from_file(RsNge100._CONFIG)
        

    def _extract_data_from_file(self, filename: str, encoding: str = "utf8") -> Dict[str, str]:
        """Extract data from filename

        Args:
            filename (str): [description]
            encoding (str, optional): [description]. Defaults to "utf8".

        Returns:
            Dict[str, str]: [description]
        """        
        with open(filename, encoding=encoding) as f:
            config = json.load(f)
            return config

    def _save_config(self):
        with open(RsNge100._CONFIG, 'w') as f:
            json.dump(self._config, f)


if __name__ == "__main__":
    rs = RsNge100()
    rs.set_parameter(Chanels.CH1, ParamTypes.VOLTAGE, 27)
    rs.set_parameter(Chanels.CH1, ParamTypes.CURRENT, 0.5)

    rs.set_supply(Chanels.CH1, SupplyStates.ENABLE)
    time.sleep(5)
    rs.set_supply(Chanels.CH1, SupplyStates.DISABLE)
