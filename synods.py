#-*- coding: utf-8 -*-
import requests
import json
from LogManager import log
import BotConfig
import taskmgr
import urllib3
import synobotLang

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SynoDownloadStation:
    instance_var = None

    STATUS_COLOR_MAP = {
        'downloading': 0x00FF00,
        'stopped': 0xFF0000,
        'paused': 0x1E90FF,
        'finishing': 0x00CED1,
        'finished': 0xFFD700,
        'error': 0xFF4500,
        'delete': 0x808080
    }

    def __init__(self):
        self.cfg = BotConfig.BotConfig().instance()
        self.dsm_login_flag = False
        self.auth_cookie = None
        self.dsm_id = ''
        self.dsm_pw = ''
        self.DSMOtpHandler = None

        self.task_mgr = taskmgr.TaskMgr().instance()
        self.task_mgr.AddNotiCallback(self.TaskNotiCallback)
        self.lang = synobotLang.synobotLang().instance()

    @classmethod
    def instance(cls):
        if cls.instance_var is None:
            cls.instance_var = SynoDownloadStation()
        return cls.instance_var

    def send_discord_message(self, title, status, size_str, username):
        webhook_url = self.cfg.GetDiscordWebhookUrl()
        if not webhook_url:
            return

        color = self.STATUS_COLOR_MAP.get(status, 0xD3D3D3)
        status_kr = self.lang.GetSynoDsLang(status)

        embed = {
            "title": "다운로드 작업 알림",
            "color": color,
            "fields": [
                {"name": "상태", "value": status_kr, "inline": False},
                {"name": "이름", "value": title, "inline": False},
                {"name": "크기", "value": size_str, "inline": False},
                {"name": "사용자", "value": username, "inline": False},
            ]
        }

        payload = {"embeds": [embed]}
        headers = {"Content-Type": "application/json"}

        try:
            requests.post(webhook_url, json=payload, headers=headers)
        except requests.exceptions.RequestException as e:
            log.error(f"Failed to send Discord notification: {e}")

    def DsmLogin(self, id, pw, otp_code=None):
        url = f"{self.cfg.GetDSDownloadUrl()}/webapi/auth.cgi"
        params = {
            'api': 'SYNO.API.Auth',
            'method': 'login',
            'version': '3',
            'account': id,
            'passwd': pw,
            'session': 'DownloadStation',
            'format': 'sid'
        }
        if otp_code:
            params['otp_code'] = otp_code

        try:
            res = requests.get(url, params=params, verify=self.cfg.IsUseCert())
            return True, res
        except requests.exceptions.RequestException as e:
            log.error(f"DSM Login request error: {e}")
            return False, str(e)

    def GetTaskList(self):
        if not self.dsm_login_flag:
            log.warning("DSM not logged in")
            return

        url = f"{self.cfg.GetDSDownloadUrl()}/webapi/DownloadStation/task.cgi"
        params = {
            'api': 'SYNO.DownloadStation.Task',
            'method': 'list',
            'version': '1'
        }

        try:
            res = requests.get(url, params=params, cookies=self.auth_cookie, verify=self.cfg.IsUseCert())
            res.raise_for_status()
            data = res.json()

            if data.get('success'):
                tasks = data.get('data', {}).get('tasks', [])
                self.CheckTaskList(tasks)
            else:
                log.error("Failed to fetch task list.")

        except requests.exceptions.RequestException as e:
            log.error(f"Task list request error: {e}")

    def CheckTaskList(self, tasks):
        task_id_list = []

        for task in tasks:
            id = task['id']
            title = task.get('title', 'Unknown')
            size = task.get('size', 0)
            user = task.get('username', 'Unknown')
            status = task.get('status', 'Unknown')

            self.task_mgr.InsertOrUpdateTask(id, title, size, user, status)
            task_id_list.append(id)

        self.task_mgr.CheckRemoveTest(task_id_list)

    def TaskNotiCallback(self, task_id, title, size, user, status):
        log.info("Task Monitor : %s, %s, %.2fGB, %s, %s", task_id, title, size/(1024*1024*1024), user, status)
        size_str = f"{round(size / (1024 * 1024 * 1024), 2)}GB" if size > 0 else "Unknown"
        self.send_discord_message(title, status, size_str, user)

    def GetTaskDetail(self):
        self.GetTaskList()

    def GetStatistic(self):
        if not self.dsm_login_flag:
            log.warning("DSM not logged in")
            return

        url = f"{self.cfg.GetDSDownloadUrl()}/webapi/DownloadStation/statistic.cgi"
        params = {
            'api': 'SYNO.DownloadStation.Statistic',
            'method': 'getinfo',
            'version': '1'
        }

        try:
            res = requests.get(url, params=params, cookies=self.auth_cookie, verify=self.cfg.IsUseCert())
            res.raise_for_status()
            data = res.json()

            if data.get('success'):
                info = data.get('data', {})
                msg = f"Download Speed: {info.get('speed_download', 0)} B/s, Upload Speed: {info.get('speed_upload', 0)} B/s"
                self.send_discord_message("DownloadStation Statistics", msg, "", "")
            else:
                log.error("Failed to fetch statistics.")

        except requests.exceptions.RequestException as e:
            log.error(f"Statistic request error: {e}")

