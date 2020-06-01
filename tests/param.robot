*** Settings ***
Library         ../rs_nge100.py
Library         rs_nge100.RsNge100
Library         BuiltIn
Library         Dialogs


*** Keywords ***
Set param
    [Arguments]     ${chanel}       ${param}       ${value}
    Set Parameter   ${chanel}       ${param}       ${value}

Set supply state
    [Arguments]     ${chanel}       ${state}
    Set supply   ${chanel}       ${state}

*** Test Cases ***
Set voltage value
    ${lib}=    Get Library Instance    rs_nge100
    Set param   ${lib.Chanels.CH1}  ${lib.ParamTypes.VOLTAGE }  ${27}

Enable chanel 1 supply
    ${lib}=    Get Library Instance    rs_nge100
    Set supply state   ${lib.Chanels.CH1}  ${lib.SupplyStates.ENABLE }
    Pause Execution

Disable chanel 1 supply
    ${lib}=    Get Library Instance    rs_nge100
    Set supply state   ${lib.Chanels.CH1}  ${lib.SupplyStates.DISABLE }



