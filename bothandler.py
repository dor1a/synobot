#-*- coding: utf-8 -*-

import sys
import time
import json
import single
import synods
import ThreadTimer
import BotConfig
import synobotLang
import OtpHandler
import requests
from LogManager import log

class BotHandler(single.SingletonInstane):
    dsdown_task_monitor = None
    ds = None

    cur_mode = ''

    cfg = None
    lang = None

    otp_input = False
    otp_code = ''

    try_login_cnt = 0

    otp_handler = None

    def InitBot(self):
        self.cfg = BotConfig.BotConfig().instance()
        self.lang = synobotLang.synobotLang().instance()
        self.otp_handler = OtpHandler.OtpHandler().instance()
        self.otp_handler.InitOtp(self.cfg.GetOtpSecret())

        self.ds = synods.SynoDownloadStation().instance()

        self.dsdown_task_monitor = ThreadTimer.ThreadTimer(10, self.ds.GetTaskList)
        self.dsdown_task_monitor.start()

        self.StartDsmLogin()

    def send_discord_message(self, text, color=0x00ff00):
        webhook_url = self.cfg.GetDiscordWebhookUrl()
        if not webhook_url:
            print("Discord Webhook URL not set.")
            return

        embed = {
            "title": "Synobot Notification",
            "description": text,
            "color": color
        }

        payload = {"embeds": [embed]}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(webhook_url, json=payload, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to send Discord notification: {e}")

    def StopTaskMonitor(self):
        if self.dsdown_task_monitor:
            self.dsdown_task_monitor.cancel()

    def StartInputLoginId(self):
        log.info('Start Input ID Flow')
        self.cur_mode = 'input_id'
        self.send_discord_message(self.lang.GetBotHandlerLang('input_login_id'), color=0x3498db)

    def StartInputPW(self):
        log.info("Start Input PW Flow")
        self.cur_mode = 'input_pw'
        self.send_discord_message(self.lang.GetBotHandlerLang('input_login_pw'), color=0x3498db)

    def StartInputOTP(self):
        log.info("Start Input OTP Flow")
        self.cur_mode = 'input_otp'
        self.send_discord_message(self.lang.GetBotHandlerLang('input_login_otp'), color=0x3498db)

    def StartDsmLogin(self, msg_silent=False):
        retry_cnt = self.cfg.GetDsmRetryLoginCnt()

        log.info('StartDsmLogin, try_login_cnt:%d, retry_cnt:%d', self.try_login_cnt, retry_cnt)

        while self.try_login_cnt < retry_cnt:
            if not self.cfg.GetDsmId():
                log.info('DSM ID is empty')
                self.StartInputLoginId()
                return False

            if not self.cfg.GetDsmPW():
                log.info('DSM PW is empty')
                self.StartInputPW()
                return False

            id = self.cfg.GetDsmId()
            pw = self.cfg.GetDsmPW()

            otp_code = self.otp_handler.GetOtp() if not self.otp_code else self.otp_code

            res, content = self.ds.DsmLogin(id, pw, otp_code)

            if not res:
                log.info('DSM Login fail, API request fail')
                self.try_login_cnt += 1
                time.sleep(3)
                continue

            if content.status_code != 200:
                log.warn("DSM Login Request fail")
                self.try_login_cnt += 1
                time.sleep(3)
                continue

            json_data = json.loads(content.content.decode('utf-8'))

            if not json_data:
                log.info('DS API Response content is none')
                self.try_login_cnt += 1
                time.sleep(3)
                continue

            if not json_data.get('success'):
                errcode = json_data['error']['code']
                if errcode == 105:
                    log.info('105 error, session expired')
                    self.send_discord_message(self.lang.GetBotHandlerLang('dsm_session_expire'), color=0xff0000)
                    return False
                elif errcode == 400:
                    log.info('400 error, id or pw invalid')
                    self.send_discord_message(self.lang.GetBotHandlerLang('dsm_invalid_id_pw'), color=0xff0000)
                    self.StartInputPW()
                    return False
                elif errcode == 401:
                    log.info('401 error, account disabled')
                    self.send_discord_message(self.lang.GetBotHandlerLang('dsm_account_disable'), color=0xff0000)
                    return False
                elif errcode in [402, 403, 404]:
                    log.info('%d error, OTP required', errcode)
                    self.StartInputOTP()
                    return False

            self.ds.auth_cookie = content.cookies
            self.ds.dsm_login_flag = True
            self.try_login_cnt = 0
            self.ds.dsm_id = id
            self.ds.dsm_pw = pw
            self.ds.DSMOtpHandler = self.otp_handler

            if not msg_silent:
                self.send_discord_message(self.lang.GetBotHandlerLang('dsm_login_succ'), color=0x00ff00)
            return True

        self.send_discord_message(self.lang.GetBotHandlerLang('dsm_login_fail_exit'), color=0xff0000)
        log.info('DSM Login Fail!!')
        sys.exit()
        return False

