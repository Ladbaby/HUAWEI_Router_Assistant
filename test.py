import requests
import xml.etree.ElementTree as ET
import hashlib
import base64
import os


from notifypy import Notify

class Router_HW:
    def __init__(
        self, 
        login_admin_user = "admin", 
        login_admin_password = "iamlocked",
        router_ip = "192.168.8.1"
    ) -> None:
        os.environ['NO_PROXY'] = router_ip
        self.session_url = 'http://' + router_ip + '/api/webserver/SesTokInfo'
        self.status_url = 'http://' + router_ip + '/api/monitoring/status'
        self.traffic_statistics_url = 'http://' + router_ip + '/api/monitoring/traffic-statistics'
        self.host_info_url = 'http://' + router_ip + '/api/system/HostInfo'
        self.device_signal_url = 'http://' + router_ip + '/api/device/signal'
        self.login_url = 'http://' + router_ip + '/api/user/login'
        self.token_url = 'http://' + router_ip + '/api/webserver/token'
        self.challenge_login_url = 'http://' + router_ip + '/api/user/challenge_login'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51',
            "__requestverificationtoken": ""
        }
        self.params = {
            "Username": "",
            "Password": "",
            "password_type": "4",
        }
        self.cookies = {"SessionID": ""}

        self.LOGIN_ADMIN_USER = login_admin_user
        self.LOGIN_ADMIN_PASSWORD = login_admin_password
        # Calculate SHA256 hash
        self.login_admin_password_sha256_hash = hashlib.sha256(self.LOGIN_ADMIN_PASSWORD.encode()).hexdigest()
        # Encode the SHA256 hash using base64
        self.login_admin_password_base64_encoded = base64.b64encode(self.login_admin_password_sha256_hash.encode()).decode().rstrip('\n')
        self.LOGIN_ADMIN_PASSWORD_BASE64 = self.login_admin_password_base64_encoded

        self.if_already_notify = False
        self.previous_battery_status = ""

        self.monitoring_status_dic = {}
        self.traffic_statistics_dic = {}

    def get_session_token(self):
        response_session = requests.get(self.session_url, headers=self.headers, timeout=60, verify=False)

        if response_session.status_code == 200:
            # print(response.text)
            root = ET.fromstring(response_session.text)

            # Retrieve the content within <TokInfo> tag
            self.TokInfo = root.find('TokInfo').text

            # Retrieve the content within <SesInfo> tag
            self.SesInfo = root.find('SesInfo').text
            self.cookies['SessionID'] = self.SesInfo

            admin_user_password_token = self.LOGIN_ADMIN_USER + self.LOGIN_ADMIN_PASSWORD_BASE64 + self.SesInfo
            admin_user_password_token_sha256_hash = hashlib.sha256(admin_user_password_token.encode()).hexdigest()
            self.admin_user_password_token_base64 = base64.b64encode(admin_user_password_token_sha256_hash.encode()).decode().rstrip('\n')

            # self.headers["__RequestVerificationToken"] = self.TokInfo
            # self.headers["Cookie"] = self.SesInfo
            # self.params["Username"] = self.LOGIN_ADMIN_USER
            # self.params["Password"] = self.admin_user_password_token_base64
            
        else:
            print("Request 'get_session_token' with status code:", response_session.status_code)

    def get_status(self):
        self.get_session_token()
        response_status = requests.get(self.status_url, headers=self.headers, timeout=60, verify=False, cookies=self.cookies)
        if response_status.status_code == 200:
            with open('status.xml', 'w') as f:
                f.write(response_status.text)
            root = ET.fromstring(response_status.text)

            # for key in root.iter():
            #     print(key.tag, key.text)
            self.BatteryStatus = root.find('BatteryStatus').text
            self.BatteryStatusStr = "Charging" if self.BatteryStatus == "1" else "Not Charging"
            self.BatteryPercent = int(root.find('BatteryPercent').text)

            sim_lock_status = int(root.find('simlockStatus').text)
            wifi_connection_status = int(root.find('WifiConnectionStatus').text)

            self.current_wifi_user = int(root.find('CurrentWifiUser').text)

            connection_status = int(root.find('ConnectionStatus').text)

            self.signal_strength = int(root.find('SignalIcon').text)
            self.max_signal_strength = int(root.find('maxsignal').text)

            current_network_type = int(root.find('CurrentNetworkType').text)

            primary_dns = root.find('PrimaryDns').text
            secondary_dns = root.find('SecondaryDns').text
            primary_ipv6_dns = root.find('PrimaryIPv6Dns').text
            secondary_ipv6_dns = root.find('SecondaryIPv6Dns').text

            # process battery status
            if self.previous_battery_status != self.BatteryStatus:
                self.if_already_notify = False
                self.previous_battery_status = self.BatteryStatus

            if self.BatteryPercent > 80 and self.BatteryStatus == "1" and not self.if_already_notify:
                self.if_already_notify = True 
                notification = Notify()
                notification.title = "HUAWEI Mobile WiFi 3 Pro finished charging"
                notification.message = 'Battery level: ' + str(self.BatteryPercent) + "%\n" + 'Status: ' + self.BatteryStatusStr
                notification.icon = 'app/resource/images/icons/battery_over_80.ico'
                notification.send(block=False)
            elif self.BatteryPercent < 30 and self.BatteryStatus == "0" and not self.if_already_notify:
                self.if_already_notify = True 
                notification = Notify()
                notification.title = "HUAWEI Mobile WiFi 3 Pro need charging"
                notification.message = 'Battery level: ' + str(self.BatteryPercent) + "%\n" + 'Status: ' + self.BatteryStatusStr
                notification.icon = 'app/resource/images/icons/battery_below_30.ico'
                notification.send(block=False)

            # process sim lock status
            self.sim_lock_status_str = "Locked" if sim_lock_status == 1 else "Unlocked"

            # process wifi connection status
            self.wifi_connection_status_dic = {
                7: "Network access not allowed",
                11: "Network access not allowed",
                14: "Network access not allowed",
                37: "Network access not allowed",
                12: "Connection failed, roaming not allowed",
                13: "Connection failed, roaming not allowed",
                201: "Connection failed, bandwidth exceeded",
                900: "Connecting",
                901: "Connected",
                902: "Disconnected",
                903: "Disconnecting",
                904: "Connection failed or disabled"
            }
            self.wifi_connection_status_str = self.wifi_connection_status_dic[wifi_connection_status] if wifi_connection_status in self.wifi_connection_status_dic.keys() else "Connection failed, the profile is invalid"

            # process connection status
            self.connection_status_str = self.wifi_connection_status_dic[connection_status] if connection_status in self.wifi_connection_status_dic.keys() else "Connection failed, the profile is invalid"

            # process network type
            self.network_type_dic = {
                0: "No Service",
                1: "GSM",
                2: "GPRS (2.5G)",
                3: "EDGE (2.75G)",
                4: "WCDMA (3G)",
                5: "HSDPA (3G)",
                6: "HSUPA (3G)",
                7: "HSPA (3G)",
                8: "TD-SCDMA (3G)",
                9: "HSPA+ (4G)",
                10: "EV-DO rev. 0",
                11: "EV-DO rev. A",
                12: "EV-DO rev. B",
                13: "1xRTT",
                14: "UMB",
                15: "1xEVDV",
                16: "3xRTT",
                17: "HSPA+ 64QAM",
                18: "HSPA+ MIMO",
                19: "LTE (4G)",
                41: "UMTS (3G)",
                44: "HSPA (3G)",
                45: "HSPA+ (3G)",
                46: "DC-HSPA+ (3G)",
                64: "HSPA (3G)",
                65: "HSPA+ (3G)",
                101: "LTE (4G)"
            }
            self.network_type_str = self.network_type_dic[current_network_type] if current_network_type in self.network_type_dic.keys() else "Unknown Connection Type"

            # update monitoring status dic
            self.monitoring_status_dic["Battery Percent"] = self.BatteryPercent
            self.monitoring_status_dic["Sim Lock Status"] = self.sim_lock_status_str
            self.monitoring_status_dic["Wifi Connection Status"] = self.wifi_connection_status_str
            self.monitoring_status_dic["Connection Status"] = self.connection_status_str
            self.monitoring_status_dic["Network Type"] = self.network_type_str
            self.monitoring_status_dic["Signal Strength"] = self.signal_strength
            self.monitoring_status_dic["Max Signal Strength"] = self.max_signal_strength
            self.monitoring_status_dic["Current Wifi User"] = self.current_wifi_user
            self.monitoring_status_dic["Primary DNS"] = primary_dns
            self.monitoring_status_dic["Secondary DNS"] = secondary_dns
            self.monitoring_status_dic["Primary IPv6 DNS"] = primary_ipv6_dns
            self.monitoring_status_dic["Secondary IPv6 DNS"] = secondary_ipv6_dns

        else:
            print("Request 'get_status' failed with status code:", response_status.status_code)

    def get_host_info(self):
        self.get_session_token()
        response_status = requests.get(self.device_signal_url, headers=self.headers, timeout=60, verify=False, cookies=self.cookies)
        if response_status.status_code == 200:
            with open('device_signal.xml', 'w') as f:
                f.write(response_status.text)

    def login(self):
        self.get_session_token()
        response_status = requests.get(
            self.login_url,
            headers=self.headers, 
            params=self.params, 
            timeout=60, 
            verify=False
        )
        if response_status.status_code == 200:
            with open('login.xml', 'w') as f:
                f.write(response_status.text)

    def get_token(self):
        self.get_status()
        self.get_session_token()
        response_status = requests.get(
            self.token_url, headers=self.headers, timeout=60, verify=False, cookies=self.cookies
        )
        if response_status.status_code == 200:
            with open('get_token.xml', 'w') as f:
                f.write(response_status.text)

            root = ET.fromstring(response_status.text)
            self.headers["__requestverificationtoken"] = root.find('token').text

    def challenge_login(self):
        self.get_session_token()
        response_status = requests.get(
            self.challenge_login_url, headers=self.headers, timeout=60, verify=False, cookies=self.cookies
        )
        if response_status.status_code == 200:
            with open('challenge_login.xml', 'w') as f:
                f.write(response_status.text)


    def get_battery_percent(self):
        # self.get_status()
        return self.BatteryPercent

    def get_battery_status(self):
        # self.get_status()
        return self.BatteryStatusStr

    def get_battery_icon_path(self):
        battery_percent = self.get_battery_percent()
        if battery_percent > 80:
            return 'app/resource/images/icons/battery_over_80.ico'
        elif 50 < battery_percent <= 80:
            return 'app/resource/images/icons/battery_50_to_80.ico'
        elif 30 < battery_percent <= 50:
            return 'app/resource/images/icons/battery_30_to_50.ico'
        elif battery_percent <= 30:
            return 'app/resource/images/icons/battery_below_30.ico'

    def update_monitoring_status(self):
        self.get_status()
        
    def get_monitoring_status_dic(self):
        return self.monitoring_status_dic


if __name__ == "__main__":
    router = Router_HW()
    router.get_status()
    router.get_token()
    router.challenge_login()


