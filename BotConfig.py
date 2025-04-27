#-*- coding: utf-8 -*-

import sys
import os
import socket
import single

class BotConfig(single.SingletonInstane):
    dsm_id = ""
    dsm_pw = ""
    log_size = 0
    log_count = 0
    dsm_url = ''
    ds_download_port = 80
    dsm_cert = True
    dsm_retry_login = 10
    dsm_task_auto_delete = False
    synobot_lang = 'ko_kr'
    tor_watch_path = ''
    execute_path = ""
    host_name = ''
    otp_secret = ''
    log_print = False
    discord_webhook_url = ''

    def __init__(self, *args, **kwargs):
        self.dsm_id = os.environ.get('DSM_ID', '')
        self.dsm_pw = os.environ.get('DSM_PW', '')

        self.log_size = int(os.environ.get('LOG_MAX_SIZE', '50'))
        self.log_count = int(os.environ.get('LOG_COUNT', '5'))

        self.dsm_url = os.environ.get('DSM_URL', 'https://DSM_IP_OR_URL')
        self.ds_download_port = os.environ.get('DS_PORT', '8000')

        if os.environ.get('DSM_CERT', '1') == '0':
            self.dsm_cert = False

        self.dsm_retry_login = int(os.environ.get('DSM_RETRY_LOGIN', '10'))

        if os.environ.get('DSM_AUTO_DEL', '0') == '1':
            self.dsm_task_auto_delete = True

        self.synobot_lang = os.environ.get('SYNO_LANG', 'ko_kr')
        self.tor_watch_path = os.environ.get('DSM_WATCH', '')

        temp_path = os.path.split(sys.argv[0])
        self.execute_path = temp_path[0]
        self.host_name = socket.gethostname()

        self.otp_secret = os.environ.get('DSM_OTP_SECRET', '')

        if os.environ.get('DOCKER_LOG', '1') == '1':
            self.log_print = True

        self.discord_webhook_url = os.environ.get('DC_WEBHOOK_URL', '')

    def GetDsmId(self):
        return self.dsm_id

    def GetDsmPW(self):
        return self.dsm_pw

    def SetDsmPW(self, pw):
        self.dsm_pw = pw

    def GetLogSize(self):
        return self.log_size

    def GetLogCount(self):
        return self.log_count

    def GetDSDownloadUrl(self):
        return self.dsm_url + ":" + self.ds_download_port

    def IsUseCert(self):
        return self.dsm_cert

    def GetDsmRetryLoginCnt(self):
        return int(self.dsm_retry_login)

    def IsTaskAutoDel(self):
        return self.dsm_task_auto_delete

    def GetSynobotLang(self):
        return self.synobot_lang

    def GetTorWatch(self):
        return self.tor_watch_path

    def GetExecutePath(self):
        return self.execute_path

    def GetHostName(self):
        return self.host_name

    def GetOtpSecret(self):
        return self.otp_secret

    def GetLogPrint(self):
        return self.log_print

    def GetDiscordWebhookUrl(self):
        return self.discord_webhook_url

