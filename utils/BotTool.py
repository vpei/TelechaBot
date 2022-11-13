# -*- coding: utf-8 -*-
# @Time    : 8/22/22 7:48 PM
# @FileName: Model.py
# @Software: PyCharm
# @Github    ：sudoskys
import pathlib
from pathlib import Path

import rtoml
import time
import json

from rich.console import Console

from telebot.asyncio_handler_backends import State, StatesGroup


class userStates(StatesGroup):
    answer = State()  # states group should contain states
    answer2 = State()
    is_start = State()


def load_csonfig():
    global _csonfig
    with open("config.json", encoding="utf-8") as f:
        _csonfig = json.load(f)


def save_csonfig():
    with open("config.json", "w", encoding="utf8") as f:
        json.dump(_csonfig, f, indent=4, ensure_ascii=False)


def dict_update(raw, new):
    dict_update_iter(raw, new)
    dict_add(raw, new)


def dict_update_iter(raw, new):
    for key in raw:
        if key not in new.keys():
            continue
        if isinstance(raw[key], dict) and isinstance(new[key], dict):
            dict_update(raw[key], new[key])
        else:
            raw[key] = new[key]


def dict_add(raw, new):
    update_dict = {}
    for key in new:
        if key not in raw.keys():
            update_dict[key] = new[key]

    raw.update(update_dict)


class botWorker(object):
    def __init__(self):
        pass

    @staticmethod
    async def delmsg(chat, message):
        from Bot.Controller import clientBot
        bot, config = clientBot().botCreate()
        await bot.delete_message(chat, message)
        # aioschedule.clear(message * abs(chat))

    @staticmethod
    async def un_restrict(message, bot, groups, un_restrict_all=False):
        if un_restrict_all:
            await bot.restrict_chat_member(groups, message.from_user.id, can_send_messages=True,
                                           can_send_media_messages=True,
                                           can_send_other_messages=True,
                                           can_pin_messages=True,
                                           can_change_info=True,
                                           can_send_polls=True,
                                           can_invite_users=True,
                                           can_add_web_page_previews=True,
                                           )
        else:
            await bot.restrict_chat_member(groups, message.from_user.id, can_send_messages=True,
                                           can_send_media_messages=True,
                                           can_send_other_messages=True,
                                           can_send_polls=True,
                                           )

    @staticmethod
    async def send_ban(message, bot, groups):
        msgss = await bot.send_message(groups,
                                       f"刚刚{message.from_user.id}没有通过验证，已经被扭送月球...！"
                                       f"\n用户12分钟后自动从黑名单中被保释")
        return msgss

    @staticmethod
    async def unbanUser(bot, chat, user):
        msgss = await bot.unban_chat_member(chat, user_id=user, only_if_banned=True)
        print("执行了移除黑名单:" + str(user))
        # aioschedule.clear(user * abs(chat))
        return msgss

    @staticmethod
    async def send_ok(message, bot, groups, well_unban):
        # if well_unban:
        #     info = "完全解封"
        # else:
        #     info = "给予普通权限"
        user = botWorker.convert(message.from_user.id)
        msgss = await bot.send_message(groups,
                                       f"刚刚{user}通过了验证！",
                                       parse_mode='MarkdownV2')
        return msgss

    @staticmethod
    def new_member_checker(msg):
        need = True
        old = msg.old_chat_member
        new = msg.new_chat_member
        info = None
        # 机器人
        if old.user.is_bot:
            need = False
        if new.user.is_bot:
            # print(new.status)
            need = False
            if new.status in ["member"] and old.status not in ["member"]:
                userName = botWorker.convert(msg.from_user.first_name)
                botName = botWorker.convert(new.user.username)
                info = {"text": f"{userName}向群组添加了同类 {botName}", "id": str(new.user.id),
                        "group": str(msg.chat.id)}
        if msg.from_user.is_bot:
            need = False
        # 被踢出的
        if new.status in ["kicked", 'left']:
            need = False
        # 被禁言的
        if new.status in ["restricted"] and old.status in ["member", 'restricted'] and msg.old_chat_member.is_member:
            need = False
        # 成员变动
        if msg.old_chat_member.is_member:
            need = False
        # 管理变动处理
        if old.status in ["administrator", "creator"] or new.status in ["administrator", "left", "creator"]:
            need = False
        return need, info

    @staticmethod
    def convert(texts):
        text = str(texts)
        chars = "_*[]()~`>#+-=|{','}.!'"
        for c in chars:
            text = text.replace(c, "\\" + c)
        # In all other places characters '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{',
        # '}', '.', '!' must be escaped with the preceding character '\'.
        return text

    @staticmethod
    def get_model(cls):
        load_csonfig()
        if _csonfig.get("Model") is None:
            _csonfig["Model"] = {}
            save_csonfig()
        Model = _csonfig.get("Model").get(str(cls))
        if Model is None:
            Model = "数学题库"
        return Model

    @staticmethod
    def AntiSpam(group_id, isOn: bool):
        load_csonfig()
        if _csonfig.get("antiSpam") is None:
            _csonfig["antiSpam"] = {}
            save_csonfig()
        OK = False
        if not (isOn is None):
            _csonfig["antiSpam"][str(group_id)] = isOn
            OK = True
        save_csonfig()
        return OK

    @staticmethod
    def casSystem(group_id, isOn: bool):
        load_csonfig()
        if _csonfig.get("casSystem") is None:
            _csonfig["casSystem"] = {}
            save_csonfig()
        OK = False
        if not (isOn is None):
            _csonfig["casSystem"][str(group_id)] = isOn
            OK = True
        save_csonfig()
        return OK

    @staticmethod
    def set_model(group_id, model=None):
        load_csonfig()
        if _csonfig.get("Model") is None:
            _csonfig["Model"] = {}
            save_csonfig()
        OK = False
        if not (model is None):
            _csonfig["Model"][str(group_id)] = model
            OK = True
        save_csonfig()
        return OK

    @staticmethod
    def get_difficulty(cls):
        load_csonfig()
        if _csonfig.get("difficulty_limit") is None:
            _csonfig["difficulty_limit"] = {}
            save_csonfig()
        if _csonfig.get("difficulty_min") is None:
            _csonfig["difficulty_min"] = {}
            save_csonfig()
        limit = _csonfig.get("difficulty_limit").get(str(cls))
        mina = _csonfig.get("difficulty_min").get(str(cls))
        if limit is None:
            limit = 7
        else:
            limit = "".join(list(filter(str.isdigit, limit)))
        if mina is None:
            mina = 1
        else:
            mina = "".join(list(filter(str.isdigit, mina)))
        return mina, limit

    @staticmethod
    def set_difficulty(group_id, difficulty_limit=None, difficulty_min=None):
        load_csonfig()
        if _csonfig.get("difficulty_limit") is None:
            _csonfig["difficulty_limit"] = {}
            save_csonfig()
        if _csonfig.get("difficulty_min") is None:
            _csonfig["difficulty_min"] = {}
            save_csonfig()
        set_difficulty_limit = False
        set_difficulty_min = False
        if not (difficulty_limit is None):
            _csonfig["difficulty_limit"][str(group_id)] = difficulty_limit
            set_difficulty_limit = True
        if not (difficulty_min is None):
            _csonfig["difficulty_min"][str(group_id)] = difficulty_min
            set_difficulty_min = True
        save_csonfig()
        return set_difficulty_min, set_difficulty_limit

    @staticmethod
    def extract_arg(arg):
        return arg.split()[1:]

    @staticmethod
    async def checkGroup(bot, msg, config):
        load_csonfig()
        if _csonfig.get("whiteGroupSwitch"):
            if int(msg.chat.id) in _csonfig.get("whiteGroup") or abs(int(msg.chat.id)) in _csonfig.get(
                    "whiteGroup"):
                return True
            else:
                if hasattr(config.ClientBot, "contact_details"):
                    contact = botWorker.convert(config.ClientBot.contact_details)
                else:
                    contact = "There is no reserved contact information."
                info = f"Bot开启了白名单模式，有人将我添加到此群组，但该群组不在我的白名单中...."
                f"请向所有者申请权限...."
                f"\nContact details:{contact}"
                f'添加白名单命令:`/addwhite {msg.chat.id}`'
                await bot.send_message(msg.chat.id,
                                       botWorker.convert(info),
                                       parse_mode='MarkdownV2')
                await bot.leave_chat(msg.chat.id)
                return False
        else:
            return True
class GroupStrategy(object):
    @staticmethod
    def GetGroupStrategy(group_id: str) -> dict:
        load_csonfig()
        default = {
            "scanUser": {
                "spam": {
                    "level": 10,
                    "command": "ban",
                    "type": "on",
                    "info": "群组策略:反垃圾系统"
                },
                "premium": {
                    "level": 5,
                    "command": "pass",
                    "type": "off",
                    "info": "群组策略:自动通过"
                },
                "nsfw": {
                    "level": 4,
                    "command": "ask",
                    "type": "off",
                    "info": "群组策略:色情审查"
                },
                "safe": {
                    "level": 1,
                    "command": "ban",
                    "type": "off",
                    "info": "群组策略:安全审查"
                },
                "suspect": {
                    "level": 2,
                    "command": "ask",
                    "type": "off",
                    "info": "群组策略:嫌疑识别"
                },
                "politics": {
                    "level": 2,
                    "command": "ask",
                    "type": "off",
                    "info": "群组策略:立场审查"
                }
            },
            "afterVerify": {
                "unpass": {
                    "level": 5,
                    "command": "cancel",
                    "type": "on",
                    "info": "不通过留看"
                }
            }
        }
        if _csonfig.get("GroupStrategy"):
            if _csonfig["GroupStrategy"].get(str(group_id)):
                dict_update(default, _csonfig["GroupStrategy"][str(group_id)])
                return default
            else:
                _csonfig["GroupStrategy"][str(group_id)] = default
                save_csonfig()
                return default
        else:
            _csonfig["GroupStrategy"] = {}
            _csonfig["GroupStrategy"][str(group_id)] = default
            save_csonfig()
            return default

    @staticmethod
    def SetScanUserStrategy(group_id: str, key, tables):
        """
        暂时没有用也没有测试过的类，请注意
        :param group_id:
        :param key:
        :param tables:
        :return:
        """
        _Setting = botWorker.GetGroupStrategy(group_id=group_id)
        if _Setting["scanUser"].get(key):
            _Setting["scanUser"][key] = tables
            _csonfig["GroupStrategy"][str(group_id)] = _Setting
            save_csonfig()

    @staticmethod
    def get_door_strategy():
        return {"spam": False, "premium": False, "nsfw": False, "suspect": False, "safe": False, "politics": False}


class yamler(object):
    # sudoskys@github
    def __init__(self):
        self.debug = False
        self.home = Path().cwd()

    def debug(self, log):
        if self.debug:
            print(log)

    @staticmethod
    def rm(top):
        Path(top).unlink()


class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


class Tool(object):
    def __init__(self):
        """
        基本工具类
        """
        self.console = Console(color_system='256', style=None)
        self.now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def dictToObj(self, dictObj):
        if not isinstance(dictObj, dict):
            return dictObj
        d = Dict()
        for k, v in dictObj.items():
            d[k] = self.dictToObj(v)
        return d


class ReadConfig(object):
    def __init__(self, config=None):
        """
        read some further config!

        param paths: the file path
        """
        self.config = config

    def get(self):
        return self.config

    def parseFile(self, paths):
        data = rtoml.load(open(paths, 'r'))
        self.config = Tool().dictToObj(data)
        return self.config

    def parseDict(self, data):
        self.config = Tool().dictToObj(data)
        return self.config


class Check(object):
    def __init__(self):
        self.file = [
            "/config.json",
            "/Captcha.toml",
        ]
        self.dir = [
            # "/Data",
        ]
        self.inits = [
            "/Data/whitelist.user",
            "/Data/blacklist.user",
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
    # def initConfig(self, path):
    #     with open(path, "w") as file:
    #         file.write("{}")

    def run(self):
        self.mk(self.dir, "{}", mkdir=True)
        self.mk(self.file, "{}", mkdir=False)
