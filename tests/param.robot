*** Settings ***
Library         ../rs_nge100.py
Library         rs_nge100.RsNge100
Library         test_class.py
Library         test_class.MyClass
Library         BuiltIn


*** Keywords ***
Set param
    [Arguments]     ${chanel}       ${param}       ${value}
    Set Parameter   ${chanel}       ${param}       ${value}


*** Test Cases ***
Set voltage value
    ${lib}=    Get Library Instance    rs_nge100
    Set param   ${lib.Chanels.CH1}  ${lib.ParamTypes.VOLTAGE }  ${5}

