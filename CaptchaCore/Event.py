# -*- coding: utf-8 -*-
# @Time    : 8/22/22 7:48 PM
# @FileName: Event.py
# @Software: PyCharm
# @Github    ：sudoskys
import pathlib
from pathlib import Path
import yaml
import time
import json

from rich.console import Console


def load_csonfig():
    global _csonfig
    with open("config.json", encoding="utf-8") as f:
        _csonfig = json.load(f)


def save_csonfig():
    with open("config.json", "w", encoding="utf8") as f:
        json.dump(_csonfig, f, indent=4, ensure_ascii=False)


class botWorker(object):
    def __init__(self):
        pass

    @staticmethod
    def delmsg(bot, chat, message):
        bot.delete_message(chat, message)

    @staticmethod
    def un_restrict(message, bot, groups):
        bot.restrict_chat_member(groups, message.from_user.id, can_send_messages=True,
                                 can_send_media_messages=True,
                                 can_send_other_messages=True)

    @staticmethod
    def send_ban(message, bot, groups):
        msgss = bot.send_message(groups,
                                 f"刚刚{message.from_user.first_name}没有通过验证，已经被踢出群组...加入了黑名单！\n12分钟后可以重新加入")
        return msgss

    @staticmethod
    def unbanUser(bot, chat, user):
        msgss = bot.unban_chat_member(chat, user_id=user, only_if_banned=True)
        return msgss

    @staticmethod
    def send_ok(message, bot, groups):
        msgss = bot.send_message(groups,
                                 f"刚刚{message.from_user.first_name}通过了验证！")
        return msgss


class yamler(object):
    # sudoskys@github
    def __init__(self):
        self.debug = False
        self.home = Path().cwd()

    def debug(self, log):
        if self.debug:
            print(log)

    def rm(self, top):
        Path(top).unlink()

    def read(self, path):
        if Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                result = yaml.full_load(f.read())
            return result
        else:
            raise Exception("Config dont exists in" + path)

    def save(self, path, Data):
        with open(path, 'w+', encoding='utf-8') as f:
            yaml.dump(data=Data, stream=f, allow_unicode=True)


class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


class Tool(object):
    def __init__(self):
        self.console = Console(color_system='256', style=None)
        self.now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def dictToObj(self, dictObj):
        if not isinstance(dictObj, dict):
            return dictObj
        d = Dict()
        for k, v in dictObj.items():
            d[k] = self.dictToObj(v)
        return d


class Read(object):
    def __init__(self, paths):
        data = yamler().read(paths)
        self.config = Tool().dictToObj(data)

    def get(self):
        return self.config


class Check(object):
    def __init__(self):
        self.file = [
            "/config.json",
            "/Captcha.yaml",
        ]
        self.dir = [
            # "/data",
        ]
        self.inits = [
            "/data/whitelist.user",
            "/data/blacklist.user",
        ]
        self.RootDir = str(pathlib.Path().cwd())

    def mk(self, tab, context, mkdir=True):

        for i in tab:
            if mkdir:
                pathlib.Path(self.RootDir + i).mkdir(parents=True, exist_ok=True)
            else:
                files = pathlib.Path(self.RootDir + i)
                if not files.exists():
                    files.touch(exist_ok=True)
                    if i in self.inits:
                        with files.open("w") as fs:
                            fs.write(context)

    # 禁用此函数
    def initConfig(self, path):
        with open(path, "w") as file:
            file.write("{}")

    def run(self):
        self.mk(self.dir, "{}", mkdir=True)
        self.mk(self.file, "{}", mkdir=False)
