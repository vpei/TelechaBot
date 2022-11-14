# -*- coding: utf-8 -*-
# @Time    : 11/14/22 10:08 AM
# @FileName: DataManager.py
# @Software: PyCharm
# @Github    ：sudoskys

# 这里是数据基本类
from pydantic import BaseModel, ValidationError, validator


class Commander(BaseModel):
    level: int = 1
    command: str = "off"
    type: str = "ask"
    info: str

    @validator('info', always=True)
    def check_consistency(cls, v, values):
        if v is None and values.get('data') is None:
            raise ValueError('must provide data or error')
        return v


class ScanUser(BaseModel):
    spam: Commander
    premium: Commander
    nsfw: Commander
    safe: Commander
    suspect: Commander
    politics: Commander


class afterVerify(BaseModel):
    unpass: Commander


class GroupStrategy(BaseModel):
    scanUser: ScanUser
    afterVerify: afterVerify


if __name__ == "__main__":
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
    user = GroupStrategy(**default)
    print(user.scanUser)
