# 📶 HUAWEI Router Assistant

A simple and badly-written program to display basic information of your HUAWEI Mobile Wifi 3 Pro (may support similar device), along with some useful features not provided by the official app or web interface.

## Features

- 🔋 Receive notification when your device is at low battery level or finish charging, threshold customizable
- ℹ️ Display basic information of your device, including:

    - Battery Percentage
    - Sim Lock Status
    - Wifi Connection Status
    - Signal Strength
    - Connection Status
    - Network Type
    - Max Signal Strength
    - Current Wifi User Count
    - Primary DNS
    - Secondary DNS
    - Primary IPv6 DNS
    - Secondary IPv6 DNS
    - Current Month Upload
    - Current Month Download
    - Month Duration
    - Month Last Clear Time
    - Current Day Used
    - Current Day Duration
    - Data Limit

## Implementation

The program post http request to get information from the router and parse the result.

Currently, the program is unable to perform password authentication due to lack of knowledge on the detailed secure mechanism. Thus, it can only get some of the result that do not require such authentication.

## TODO

- [ ] Record battery level
- [ ] Password authentication

## Credits

Special thanks to the following projects

- UI Libray: [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
- Inspiration: [query_huawei_wifi_router](https://github.com/zikusooka/query_huawei_wifi_router)

