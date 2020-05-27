
import pyvisa
import time
import json
import re
from pyvisa import Resource
from enum import Enum, IntEnum
from typing import Tuple, Union, Optional, Dict

# rm = pyvisa.ResourceManager()
# my_instrument = rm.open_resource('USB0::0x0AAD::0x0197::5601.1414k03-100521::INSTR')

# print(my_instrument.query('*IDN?'))
# # 'INST OUT1; OUTP ON'
# # 'INST OUT1; APPLY "6,2"'
# my_instrument.write('INST OUT1; OUTP ON')

# my_instrument.write('INST OUT1; OUTP?')
# print(my_instrument.read())

# my_instrument.write('INST OUT1; APPLY?')
# # time.sleep(1)
# print(my_instrument.read())

# time.sleep(1)
# my_instrument.write('INST OUT1; OUTP OFF')

# my_instrument.write('INST OUT1; OUTP?')
# print(my_instrument.read())


# my_instrument.write('INST?')
# print(my_instrument.read())


# my_instrument.write('OUTP:GEN OFF')
# # while True:
# #     print(my_instrument.read_bytes(1))


class CmdTypes(IntEnum):
    SetVoltageAndCurrent = 0,
    SetVolate = 1,
    SetCurrent = 2,
    GetVoltageAndCurrent = 3
    GetVoltage = 4,
    GetCurrent = 5

class Chanels(Enum):
    CH1 = "Chanel_1"
    CH2 = "Chanel_2"
    CH3 = "Chanel_3"

class ParamTypes(Enum):
    CHANEL_ID = "Id"
    VOLTAGE = "Voltage" # 'INST OUT1; APPLY "6,2"'
    CURRENT = "Current" # 'INST OUT1; APPLY "6,2"'
    OUTPUT_STATE = "OutputState" # 'INST OUT1; OUTP ON'


class RsNge100():
    def __init__(self):
        self._cmd_templates = {
            CmdTypes.SetVoltageAndCurrent: 'INST OUT{chanel}; APPLY "{vol}, {cur}"',
            CmdTypes.SetVolate: 'INST OUT{chanel}; APPLY "{voltage},2"',
            CmdTypes.SetCurrent: 'INST OUT{chanel}; APPLY "6,{cur}"',
            CmdTypes.GetVoltageAndCurrent: 'INST OUT{chanel}; APPLY?',
        }
        self._rm = pyvisa.ResourceManager()
        self._instr = self._init_instrument()
        self._config = self._init_params()

    def set_parameter(self, chanel: Chanels, param: ParamTypes, value: int ) -> None:
        cmd_type: Optional[CmdTypes] = None

        self._config[chanel.value][param.value] = value

        if param == ParamTypes.VOLTAGE or  param == ParamTypes.CURRENT:
            cmd_type = CmdTypes.SetVoltageAndCurrent
            
        if cmd_type is not None:
            packet = self._build(chanel, cmd_type)

        self._instr.write(packet)

        self._save_config()

    def _build(self, chanel: Chanels, cmd: CmdTypes) -> Optional[str]:
        'INST OUT{chanel}; OUTP ON'
        temp: Optional[str] = None
        packet: Optional[str] = None
        
        if cmd == CmdTypes.SetVolate or cmd == CmdTypes.SetCurrent or cmd == CmdTypes.SetVoltageAndCurrent:
            temp = self._cmd_templates[CmdTypes.SetVoltageAndCurrent]
            ch_config = self._config[chanel.value]
            ch = ch_config[ParamTypes.CHANEL_ID.value]
            voltage = ch_config[ParamTypes.VOLTAGE.value]
            current = ch_config[ParamTypes.CURRENT.value]

        if temp is not None:
            packet = temp.format(chanel =ch, vol = voltage, cur = current)

        return packet
   
    def enable(self):
        pass

    def disable(self):
        pass


    def _init_instrument(self) -> Resource:
        name = self._init_resource_name()
        return self._rm.open_resource(name)


    def _init_resource_name(self) -> str:
        filename = "config/usb.json"
        usb_config = self._extract_data_from_file(filename)
        vid = usb_config["VID"]
        pid = usb_config["PID"]

        names = self._rm.list_resources()
        for name in names:
            if vid in name and pid in name:
                return name

        # Change to Exception
        return False

    def _init_params(self):
        filename = "config/rs_nge100.json"
        return self._extract_data_from_file(filename)
        

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
        with open("config/rs_nge100.json", 'w') as f:
            json.dump(self._config, f)


if __name__ == "__main__":
    rs = RsNge100()
    rs.set_parameter(Chanels.CH1, ParamTypes.VOLTAGE, 5)
    rs.set_parameter(Chanels.CH1, ParamTypes.CURRENT, 3)

    rs.set_parameter(Chanels.CH2, ParamTypes.VOLTAGE, 10)


    rs.set_parameter(Chanels.CH3, ParamTypes.VOLTAGE, 20)
    rs.set_parameter(Chanels.CH3, ParamTypes.CURRENT, 0.5)
