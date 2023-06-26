import requests
import xml.etree.ElementTree as ET
import hashlib
import base64

from notifypy import Notify

class Router_HW:
    def __init__(
        self, 
        login_admin_user = "admin", 
        login_admin_password = "iamlocked",
        router_ip = "192.168.8.1"
    ) -> None:
        self.session_url = 'http://' + router_ip + '/api/webserver/SesTokInfo'
        self.status_url = 'http://' + router_ip + '/api/monitoring/status'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51'}
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

    def get_session_token(self):
        response_session = requests.get(self.session_url, headers=self.headers, timeout=60, verify=False)

        if response_session.status_code == 200:
            # print(response.text)
            root = ET.fromstring(response_session.text)

            # Retrieve the content within <TokInfo> tag
            self.TokInfo = root.find('TokInfo').text
            # print('login_server_cookie:', login_server_cookie)

            # Retrieve the content within <SesInfo> tag
            self.SesInfo = root.find('SesInfo').text
            # print('login_server_token:', login_server_token)
            self.cookies['SessionID'] = self.SesInfo

            admin_user_password_token = self.LOGIN_ADMIN_USER + self.LOGIN_ADMIN_PASSWORD_BASE64 + self.SesInfo
            admin_user_password_token_sha256_hash = hashlib.sha256(admin_user_password_token.encode()).hexdigest()
            self.admin_user_password_token_base64 = base64.b64encode(admin_user_password_token_sha256_hash.encode()).decode().rstrip('\n')
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
            self.BatteryStatusStr = "充电中" if self.BatteryStatus == "1" else "放电中"
            self.BatteryPercent = int(root.find('BatteryPercent').text)

            if self.previous_battery_status != self.BatteryStatus:
                self.if_already_notify = False
                self.previous_battery_status = self.BatteryStatus

            if self.BatteryPercent > 80 and self.BatteryStatus == "1" and not self.if_already_notify:
                self.if_already_notify = True 
                notification = Notify()
                notification.title = "华为随行WiFi 3 Pro充电已完成"
                notification.message = '当前电量：' + str(self.BatteryPercent) + "%\n" + '当前状态：' + self.BatteryStatusStr
                notification.icon = 'app/resource/images/icons/battery_over_80.ico'
                notification.send(block=False)
            elif self.BatteryPercent < 30 and self.BatteryStatus == "0" and not self.if_already_notify:
                self.if_already_notify = True 
                notification = Notify()
                notification.title = "华为随行WiFi 3 Pro电量不足"
                notification.message = '当前电量：' + str(self.BatteryPercent) + "%\n" + '当前状态：' + self.BatteryStatusStr
                notification.icon = 'app/resource/images/icons/battery_below_30.ico'
                notification.send(block=False)

        else:
            print("Request 'get_status' failed with status code:", response_status.status_code)

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
        





