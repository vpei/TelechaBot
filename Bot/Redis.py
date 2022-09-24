# -*- coding: utf-8 -*-
# @Time    : 8/22/22 9:28 PM
# @FileName: Redis.py
# @Software: PyCharm
# @Github    ：sudoskys
import time
import ast
import redis  # 导入redis 模块
import datetime

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)


# 必须需要一个创建机器人对象的类才能使用KickMember功能！

class JsonRedis(object):
    def __init__(self, interval=175):
        JsonRedis.load_tasks()
        if not _tasks.get("interval"):
            if interval:
                _tasks["interval"] = interval
                JsonRedis.save_tasks()
        if not _tasks.get("Time_id"):
            _tasks["Time_id"] = {}
            JsonRedis.save_tasks()
        if not _tasks.get("Time_group"):
            _tasks["Time_group"] = {}
            JsonRedis.save_tasks()
        if not _tasks.get("User_group"):
            _tasks["User_group"] = {}
            JsonRedis.save_tasks()
        if not _tasks.get("super"):
            _tasks["super"] = {}
            JsonRedis.save_tasks()

    @staticmethod
    def load_tasks():
        global _tasks
        task = r.get('tasks')
        if task is not None:
            _tasks = ast.literal_eval(task)
        else:
            _tasks = {}

    @staticmethod
    def save_tasks():
        r.set('tasks', str(_tasks))

    @staticmethod
    def readUser(where, group):
        where = str(where)
        JsonRedis.load_tasks()
        if _tasks.get(where):
            oss = _tasks[where].get(str(group))
            if oss:
                return oss
            else:
                return []
        else:
            return []

    @staticmethod
    def popUser(where, group, key):
        where = str(where)
        JsonRedis.load_tasks()
        if _tasks.get(where):
            if _tasks[where][str(group)]:
                if key in _tasks[where][str(group)]:
                    _tasks[where][str(group)].pop(key)
        JsonRedis.save_tasks()

    @staticmethod
    def saveUser(where, group, key):
        where = str(where)
        JsonRedis.load_tasks()
        if _tasks.get(where):
            if _tasks[where].get(str(group)):
                if not (key in _tasks[where][str(group)]):
                    _tasks[where][str(group)].append(key)
            else:
                _tasks[where][str(group)] = []
                _tasks[where][str(group)].append(key)
        else:
            _tasks[where] = {}
            _tasks[where][str(group)] = []
            _tasks[where][str(group)].append(key)
        JsonRedis.save_tasks()

    @staticmethod
    def resign_user(userId, groupId):
        """
        注册队列
        :param userId:
        :param groupId:
        :return:
        """
        JsonRedis.load_tasks()
        key = str(int(time.time()))
        _tasks["Time_id"][key] = str(userId)
        _tasks["Time_group"][key] = str(groupId)
        JsonRedis.save_tasks()
        JsonRedis.saveUser("User_group", str(userId), key)
        return key

    @staticmethod
    def read_user(userId):
        """
        读取用户的注册键
        :param userId:
        :return:
        """
        User = _tasks["User_group"].get(str(userId))
        if User:
            if len(User) != 0:
                key = str(_tasks["User_group"].get(str(userId))[0])
                # user = _tasks["Time_id"].get(key)
                group = _tasks["Time_group"].get(key)
                return group, key
            else:
                return False, False
        else:
            return False, False

    @staticmethod
    async def remove_user(userId, groupId):
        """
        人员被移除或者退群，弹出对目标群组的验证任务
        :param userId:
        :param groupId:
        :return:
        """
        User = _tasks["User_group"].get(str(userId))
        if User:
            if len(User) != 0:
                for key, i in _tasks["Time_group"].items():
                    if i == str(groupId):
                        await JsonRedis.checker(dismiss=[key])

    @staticmethod
    async def grant_resign(userId, groupId):
        """
        提升用户并取消过期队列,解禁需要另外语句
        :param userId:
        :param groupId:
        :return:
        """
        User = _tasks["User_group"].get(str(userId))
        if User:
            if len(User) != 0:
                for key, i in _tasks["Time_group"].items():
                    if i == str(groupId):
                        await JsonRedis.checker(tar=[key])
                        return key
                    else:
                        return "没有相关记录"
            return "错误:你没有在等待队列中"
        # JsonRedis().remove_user(userId, groupId)
        # JsonRedis.saveUser("super", str(userId), str(groupId))
        # else:
        #     key = _tasks["User_group"].get(str(userId))[0]
        #     # groupId = _tasks["Time_group"].get(key)
        #     # JsonRedis.saveUser("super", str(userId), str(groupId))
        #     await JsonRedis.checker(tar=[key])

    @staticmethod
    async def checker(tar=None, fail_user=None, dismiss=None):
        """
        检查器，调用就会检查一次，弹出传入的键值，
        :param dismiss: 传入这里，弹出且不做操作
        :param tar: 传入这里，则不踢出而弹出
        :param fail_user: 传入这里，则踢出且弹出
        :return:
        """
        group = False
        user = False
        if dismiss is None:
            dismiss = []
        if tar is None:
            tar = []
        if fail_user is None:
            fail_user = []
        dealList = [] + fail_user + tar + dismiss
        # 插队key和检查过期Key
        JsonRedis.load_tasks()
        for key, item in _tasks["Time_id"].items():
            if abs(int(time.time()) - int(key)) > int(_tasks["interval"]):
                dealList.append(key)

        for key in dealList:
            try:
                user = _tasks["Time_id"].pop(str(key))
                group = _tasks["Time_group"].pop(str(key))
                _tasks["User_group"].get(str(user)).remove(str(key))
            except Exception as e:
                print(e)
            if key not in dismiss:
                from Bot.Controller import clientBot
                bot, config = clientBot().botCreate()
                if key in tar:
                    await bot.approve_chat_join_request(chat_id=group, user_id=user)
                else:
                    try:
                        if group and user:
                            await bot.delete_state(user, group)
                            await bot.decline_chat_join_request(chat_id=group, user_id=user)
                            await bot.ban_chat_member(chat_id=group, user_id=user,
                                                      until_date=datetime.datetime.timestamp(
                                                          datetime.datetime.now() + datetime.timedelta(minutes=12)))
                            await bot.send_message(user, f"验证失败，此群组会话验证需要冷却 12 分钟")
                    except Exception as e:
                        print(e)
                    # print("ban " + str(user) + str(group))
        JsonRedis.save_tasks()

    @staticmethod
    async def run_timer():
        await JsonRedis.checker()
        JsonRedis.timer()

    @staticmethod
    def timer():
        from threading import Timer
        t = Timer(3, JsonRedis.run_timer)
        t.start()

#########################################
# JsonRedis(6).add(1222, str(-52333))
#
# JsonRedis.timer()
#
# print(2)
