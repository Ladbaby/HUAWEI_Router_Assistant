import requests
import xml.etree.ElementTree as ET
import hashlib
import base64
import os
import concurrent.futures
import time

from notifypy import Notify
from .config import cfg
from.global_logger import logger

from .database import Cache

class Router_HW:
    def __init__(
        self, 
        login_admin_user = "admin", 
        login_admin_password = "password",
        router_ip = "192.168.8.1"
    ) -> None:
        os.makedirs('debug', exist_ok=True)
        os.environ['NO_PROXY'] = router_ip
        self.session_url = 'http://' + router_ip + '/api/webserver/SesTokInfo'
        self.status_url = 'http://' + router_ip + '/api/monitoring/status'
        self.traffic_statistics_url = 'http://' + router_ip + '/api/monitoring/traffic-statistics'
        self.month_statistics_url = 'http://' + router_ip + '/api/monitoring/month_statistics'
        self.start_date_url = 'http://' + router_ip + '/api/monitoring/start_date'
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

        self.monitoring_status_dic = {
            "Battery Percent": 0,
            "Sim Lock Status": "-",
            # "Wifi Connection Status": "-",
            "Signal Strength": "-",
            "Connection Status": "-",
            "Network Type": "Device offline",
            "Signal Strength": 0,
            "Max Signal Strength": 5,
            "Current Wifi User": 0,
            "Primary DNS": "-",
            "Secondary DNS": "-",
            "Primary IPv6 DNS": "-",
            "Secondary IPv6 DNS": "-",
            "Month Percentage": 0,
            "Current Month Download": "-",
            "Current Month Upload": "-",
            "Current Upload Download Raw": 0,
            "Month Duration": "-",
            "Month Last Clear Time": "-",
            "Current Day Used": "-",
            "Current Day Duration": "-",
            "Data Limit": "-",
            "Traffic Max Limit Raw": 0
        }
        self.traffic_statistics_dic = {
            "Signal Strength": 0,
            "Network Type": "Device offline",
            "Current Download Rate": "-",
            "Current Upload Rate": "-",
            "Total Upload": "-",
            "Total Download": "-",
            "Current Connect Time": "-",
            "Total Connect Time": "-"
        }
        self.month_statistics_dic = {
            "Traffic Max Limit": "-",
            "Current Upload Download": "-"
        }

        self.db = Cache()
        self.previous_status_time = 0

        self.BatteryPercent = 0
        self.BatteryStatusStr = "-"

    def get_session_token(self):
        try:
            response_session = requests.get(self.session_url, headers=self.headers, timeout=0.5, verify=False)

            if response_session.status_code == 200:
                root = ET.fromstring(response_session.text)

                # Retrieve the content within <TokInfo> tag
                self.TokInfo = root.find('TokInfo').text

                # Retrieve the content within <SesInfo> tag
                self.SesInfo = root.find('SesInfo').text
                self.cookies['SessionID'] = self.SesInfo

                # admin_user_password_token = self.LOGIN_ADMIN_USER + self.LOGIN_ADMIN_PASSWORD_BASE64 + self.SesInfo
                # admin_user_password_token_sha256_hash = hashlib.sha256(admin_user_password_token.encode()).hexdigest()
                # self.admin_user_password_token_base64 = base64.b64encode(admin_user_password_token_sha256_hash.encode()).decode().rstrip('\n')
            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(self.write_error_log, "Request 'get_session_token' failed with status code:" + response_session.status_code)
                # if cfg.get(cfg.enableLogging):
                #     logger.error("Request 'get_session_token' failed with status code:" + response_session.status_code)

        except:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(self.write_error_log, "`get_session_token` failed to reach router at " + self.session_url)
            # if cfg.get(cfg.enableLogging):
            #     logger.error("`get_session_token` failed to reach router at " + self.session_url)

    def write_debug_xml(self, response, filename):
        if cfg.get(cfg.enableLogging):
            with open('debug/' + filename + '.xml', 'w') as f:
                f.write(response.text)

    def write_error_log(self, error_message):
        if cfg.get(cfg.enableLogging):
            logger.error(error_message)

    def write_warning_log(self, warning_message):
        if cfg.get(cfg.enableLogging):
            logger.warning(warning_message)

    def get_status(self):
        self.get_session_token()
        try:
            response_status = requests.get(self.status_url, headers=self.headers, timeout=0.5, verify=False, cookies=self.cookies)
            if response_status.status_code == 200:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(self.write_debug_xml, response_status, "status")
                    # if cfg.get(cfg.enableLogging):
                    #     with open('debug/status.xml', 'w') as f:
                    #         f.write(response_status.text)
                root = ET.fromstring(response_status.text)

                try:
                    self.BatteryStatus = "0" if root.find('BatteryStatus') == None else root.find('BatteryStatus').text
                    self.BatteryStatusStr = "Charging" if self.BatteryStatus == "1" else "Not Charging"
                    self.BatteryPercent = 0 if root.find('BatteryPercent') == None else int(root.find('BatteryPercent').text)
                    # use sqlite3 to store the battery percentage history and the corresponding timestamp
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        # only write to database when time interval greater than 60 seconds
                        current_time = int(time.time())
                        if current_time - self.previous_status_time >= 60:
                            executor.submit(self.db.write_battery_history,{"timestamp": current_time, "percentage": self.BatteryPercent, "charging": self.BatteryStatus})
                            self.previous_status_time = current_time

                    # process battery status
                    if self.previous_battery_status != self.BatteryStatus:
                        self.if_already_notify = False
                        self.previous_battery_status = self.BatteryStatus

                    if cfg.get(cfg.batteryUpperBoundNotification):
                        if self.BatteryPercent > cfg.get(cfg.batteryUpperBoundThreshold) and self.BatteryStatus == "1" and not self.if_already_notify:
                            self.if_already_notify = True 
                            notification = Notify()
                            notification.title = "HUAWEI Mobile WiFi 3 Pro finished charging"
                            notification.message = 'Battery level: ' + str(self.BatteryPercent) + "%\n" + 'Status: ' + self.BatteryStatusStr
                            notification.icon = 'app/resource/images/icons/battery_over_80.ico'
                            notification.send(block=False)

                    if cfg.get(cfg.batteryLowerBoundNotification):
                        if self.BatteryPercent < cfg.get(cfg.batteryLowerBoundThreshold) and self.BatteryStatus == "0" and not self.if_already_notify:
                            self.if_already_notify = True 
                            notification = Notify()
                            notification.title = "HUAWEI Mobile WiFi 3 Pro need charging"
                            notification.message = 'Battery level: ' + str(self.BatteryPercent) + "%\n" + 'Status: ' + self.BatteryStatusStr
                            notification.icon = 'app/resource/images/icons/battery_below_30.ico'
                            notification.send(block=False)
                except:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        executor.submit(self.write_warning_log, "`get_status` failed to find battery information")
                    # logger.warning("`get_status` failed to find battery information")
                    self.BatteryStatusStr = "No battery"
                    self.BatteryPercent = 100

                sim_lock_status = int(root.find('simlockStatus').text)
                # wifi_connection_status = int(root.find('WifiConnectionStatus').text)

                self.current_wifi_user = int(root.find('CurrentWifiUser').text)

                connection_status = int(root.find('ConnectionStatus').text)

                self.signal_strength = int(root.find('SignalIcon').text)
                self.max_signal_strength = int(root.find('maxsignal').text)

                current_network_type = int(root.find('CurrentNetworkType').text)

                primary_dns = root.find('PrimaryDns').text
                secondary_dns = root.find('SecondaryDns').text
                primary_ipv6_dns = root.find('PrimaryIPv6Dns').text
                secondary_ipv6_dns = root.find('SecondaryIPv6Dns').text


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
                # self.wifi_connection_status_str = self.wifi_connection_status_dic[wifi_connection_status] if wifi_connection_status in self.wifi_connection_status_dic.keys() else "Connection failed, the profile is invalid"

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
                # self.monitoring_status_dic["Wifi Connection Status"] = self.wifi_connection_status_str
                self.monitoring_status_dic["Connection Status"] = self.connection_status_str
                self.monitoring_status_dic["Network Type"] = self.network_type_str
                self.monitoring_status_dic["Signal Strength"] = self.signal_strength
                self.monitoring_status_dic["Max Signal Strength"] = self.max_signal_strength
                self.monitoring_status_dic["Current Wifi User"] = self.current_wifi_user
                self.monitoring_status_dic["Primary DNS"] = primary_dns
                self.monitoring_status_dic["Secondary DNS"] = secondary_dns
                self.monitoring_status_dic["Primary IPv6 DNS"] = primary_ipv6_dns
                self.monitoring_status_dic["Secondary IPv6 DNS"] = secondary_ipv6_dns

                self.traffic_statistics_dic["Signal Strength"] = self.signal_strength
                self.traffic_statistics_dic["Network Type"] = self.network_type_str

                self.get_traffic_statistics()
                self.get_month_statistics()
                self.get_start_date()

                if self.monitoring_status_dic["Traffic Max Limit Raw"] != 0:
                    self.month_statistics_dic["Month Percentage"] = round(self.monitoring_status_dic["Current Upload Download Raw"] / self.monitoring_status_dic["Traffic Max Limit Raw"] * 100, 2)
                else:
                    self.month_statistics_dic["Month Percentage"] = 0

            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(self.write_error_log, "Request 'get_status' failed with status code:" + response_status.status_code)
                # if cfg.get(cfg.enableLogging):
                #     logger.error("Request 'get_status' failed with status code:" + response_status.status_code)
        except:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(self.write_error_log, "Request 'get_status' failed to reach router at " + self.session_url)
            # if cfg.get(cfg.enableLogging):
            #     logger.error("`get_status` failed to reach router at " + self.session_url)
            self.monitoring_status_dic["Battery Percent"] = 0
            self.monitoring_status_dic["Sim Lock Status"] = "-"
            # self.monitoring_status_dic["Wifi Connection Status"] = "-"
            self.monitoring_status_dic["Connection Status"] = "-"
            self.monitoring_status_dic["Network Type"] = "Device offline"
            self.monitoring_status_dic["Signal Strength"] = 0
            self.monitoring_status_dic["Max Signal Strength"] = 5
            self.monitoring_status_dic["Current Wifi User"] = 0
            self.monitoring_status_dic["Primary DNS"] = "-"
            self.monitoring_status_dic["Secondary DNS"] = "-"
            self.monitoring_status_dic["Primary IPv6 DNS"] = "-"
            self.monitoring_status_dic["Secondary IPv6 DNS"] = "-"

            self.traffic_statistics_dic["Signal Strength"] = 0
            self.traffic_statistics_dic["Network Type"] = "Device offline"

            if self.monitoring_status_dic["Traffic Max Limit Raw"] != 0:
                self.month_statistics_dic["Month Percentage"] = round(self.monitoring_status_dic["Current Upload Download Raw"] / self.monitoring_status_dic["Traffic Max Limit Raw"] * 100, 2)
            else:
                self.month_statistics_dic["Month Percentage"] = 0
            pass

    def get_traffic_statistics(self):
        self.get_session_token()
        try:
            response_status = requests.get(self.traffic_statistics_url, headers=self.headers, timeout=0.5, verify=False, cookies=self.cookies)
            if response_status.status_code == 200:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(self.write_debug_xml, response_status, "traffic_statistics")
                # if cfg.get(cfg.enableLogging):
                #     with open('debug/traffic_statistics.xml', 'w') as f:
                #         f.write(response_status.text)
                root = ET.fromstring(response_status.text)

                current_connect_time = self.calc_time(root.find('CurrentConnectTime').text)
                current_download_rate = self.calc_traffic(root.find('CurrentDownloadRate').text) + '/s'
                current_upload_rate = self.calc_traffic(root.find('CurrentUploadRate').text) + '/s'
                total_upload = self.calc_traffic(root.find('TotalUpload').text)
                total_download = self.calc_traffic(root.find('TotalDownload').text)
                total_connect_time = self.calc_time(root.find('TotalConnectTime').text)

                self.traffic_statistics_dic["Current Download Rate"] = current_download_rate
                self.traffic_statistics_dic["Current Upload Rate"] = current_upload_rate
                self.traffic_statistics_dic["Total Upload"] = total_upload
                self.traffic_statistics_dic["Total Download"] = total_download
                self.traffic_statistics_dic["Current Connect Time"] = current_connect_time
                self.traffic_statistics_dic["Total Connect Time"] = total_connect_time
            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(self.write_error_log, "Request 'get_traffic_statistics' failed with status code:" + response_status.status_code)
                # if cfg.get(cfg.enableLogging):
                #     logger.error("Request 'get_traffic_statistics' failed with status code:" + response_status.status_code)
        except:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(self.write_error_log, "Request 'get_traffic_statistics' failed to reach router at " + self.session_url)
            # if cfg.get(cfg.enableLogging):
            #     logger.error("`get_traffic_statistics` failed to reach router at " + self.session_url)
            self.traffic_statistics_dic["Current Download Rate"] = "-"
            self.traffic_statistics_dic["Current Upload Rate"] = "-"
            self.traffic_statistics_dic["Total Upload"] = "-"
            self.traffic_statistics_dic["Total Download"] = "-"
            self.traffic_statistics_dic["Current Connect Time"] = "-"
            self.traffic_statistics_dic["Total Connect Time"] = "-"

    def get_month_statistics(self):
        self.get_session_token()
        try:
            response_status = requests.get(
                self.month_statistics_url, headers=self.headers, timeout=0.5, verify=False, cookies=self.cookies
            )
            if response_status.status_code == 200:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(self.write_debug_xml, response_status, "month_statistics")
                # if cfg.get(cfg.enableLogging):
                #     with open('debug/month_statistics.xml', 'w') as f:
                #         f.write(response_status.text)
                root = ET.fromstring(response_status.text)

                current_month_download = self.calc_traffic(root.find('CurrentMonthDownload').text)
                current_month_download_raw = int(root.find('CurrentMonthDownload').text)
                current_month_upload = self.calc_traffic(root.find('CurrentMonthUpload').text)
                current_month_upload_raw = int(root.find('CurrentMonthUpload').text)
                current_upload_download_raw = current_month_upload_raw + current_month_download_raw
                month_duration = self.calc_time(root.find('MonthDuration').text)
                month_last_clear_time = root.find('MonthLastClearTime').text
                current_day_used = self.calc_traffic(root.find('CurrentDayUsed').text)
                current_day_duration = self.calc_time(root.find('CurrentDayDuration').text)

                self.monitoring_status_dic["Current Month Download"] = current_month_download
                self.monitoring_status_dic["Current Month Upload"] = current_month_upload
                self.monitoring_status_dic["Current Upload Download Raw"] = current_upload_download_raw
                self.monitoring_status_dic["Month Duration"] = month_duration
                self.monitoring_status_dic["Month Last Clear Time"] = month_last_clear_time
                self.monitoring_status_dic["Current Day Used"] = current_day_used
                self.monitoring_status_dic["Current Day Duration"] = current_day_duration
        except:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(self.write_error_log, "Request 'get_month_statistics' failed to reach router at " + self.session_url)
            # if cfg.get(cfg.enableLogging):
            #     logger.error("`get_month_statistics` failed to reach router at " + self.session_url)
            self.monitoring_status_dic["Current Month Download"] = "-"
            self.monitoring_status_dic["Current Month Upload"] = "-"
            self.monitoring_status_dic["Current Upload Download Raw"] = 0
            self.monitoring_status_dic["Month Duration"] = "-"
            self.monitoring_status_dic["Month Last Clear Time"] = "-"
            self.monitoring_status_dic["Current Day Used"] = "-"
            self.monitoring_status_dic["Current Day Duration"] = "-"
            pass
            
    def get_start_date(self):
        self.get_session_token()
        try:
            response_status = requests.get(
                self.start_date_url, headers=self.headers, timeout=0.5, verify=False, cookies=self.cookies
            )
            if response_status.status_code == 200:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(self.write_debug_xml, response_status, "start_date")
                # if cfg.get(cfg.enableLogging):
                #     with open('debug/start_date.xml', 'w') as f:
                #         f.write(response_status.text)
                root = ET.fromstring(response_status.text)

                data_limit = root.find('DataLimit').text
                traffic_max_limit = self.calc_traffic(root.find('trafficmaxlimit').text)
                traffic_max_limit_raw = int(root.find('trafficmaxlimit').text)

                self.monitoring_status_dic["Data Limit"] = data_limit
                self.month_statistics_dic["Traffic Max Limit"] = traffic_max_limit
                self.monitoring_status_dic["Traffic Max Limit Raw"] = traffic_max_limit_raw
                self.month_statistics_dic["Current Upload Download"] = self.calc_traffic(self.monitoring_status_dic["Traffic Max Limit Raw"] - self.monitoring_status_dic["Current Upload Download Raw"])
        except:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(self.write_error_log, "Request 'get_start_date' failed to reach router at " + self.session_url)
            # if cfg.get(cfg.enableLogging):
            #     logger.error("`get_start_date` failed to reach router at " + self.session_url)
            self.monitoring_status_dic["Data Limit"] = "-"
            self.month_statistics_dic["Traffic Max Limit"] = "-"
            self.monitoring_status_dic["Traffic Max Limit Raw"] = 0
            self.month_statistics_dic["Current Upload Download"] = "-"
            pass

    def calc_traffic(self, input_str):
        if int(input_str) > 1024 * 1024 * 1024:
            output = str(round(int(input_str) / 1024 / 1024 / 1024, 2)) + " GB"
        else:
            output = str(round(int(input_str) / 1024 / 1024, 2)) + " MB" if int(input_str) > 1024 * 1024 else str(round(int(input_str) / 1024, 2)) + " KB"
        return output

    def calc_time(self, seconds):
        seconds = int(seconds)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 60)
        return "%d days, %d hours, %d minutes, %d seconds" % (d, h, m, s)

    def get_battery_percent(self):
        # self.get_status()
        return self.BatteryPercent

    def get_battery_status(self):
        # self.get_status()
        return self.BatteryStatusStr

    def get_battery_icon_path(self):
        battery_percent = self.get_battery_percent()
        if battery_percent > 80:
            return ':/gallery/images/icons/battery_over_80.ico'
        elif 50 < battery_percent <= 80:
            return ':/gallery/images/icons/battery_50_to_80.ico'
        elif 30 < battery_percent <= 50:
            return ':/gallery/images/icons/battery_30_to_50.ico'
        elif battery_percent <= 30:
            return ':/gallery/images/icons/battery_below_30.ico'

    def get_traffic_statistics_dic(self):
        return self.traffic_statistics_dic

    def update_monitoring_status(self):
        self.get_status()

    def update_traffic_statistics(self):
        self.get_traffic_statistics()
        
    def get_monitoring_status_dic(self):
        return self.monitoring_status_dic

    def get_month_statistics_dic(self):
        return self.month_statistics_dic

    def get_battery_history_dic(self):
        self.db.remove_battery_history()
        battery_history_list = self.db.read_battery_history()
        battery_history_dic = {
            "time": [x[0] for x in battery_history_list],
            "battery": [x[1] for x in battery_history_list],
            "charging": [x[2] for x in battery_history_list]
        }
        return battery_history_dic

    