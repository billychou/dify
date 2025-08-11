#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_passport.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/8/11
Copyright: @三分地技术有限公司
"""
import jwt
from datetime import datetime
from datetime import UTC
from datetime import timedelta
from libs.passport import PassportService
from configs import dify_config
from icecream import ic
from werkzeug.exceptions import Unauthorized


def test_passport_service_jwt():
    """
    Test the utility of the jwt function
    """
    # UTC datetime
    exp_dt = datetime.now(UTC) + timedelta(
        minutes=dify_config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    ic(exp_dt)
    ic(exp_dt.timestamp())
    #  timezone
    exp_dt = datetime.now() + timedelta(minutes=dify_config.ACCESS_TOKEN_EXPIRE_MINUTES)
    ic(exp_dt)
    exp = int(exp_dt.timestamp())
    ic(exp)
    payload = {
        "user_id": 10,
        "exp": exp,
        "iss": dify_config.EDITION,
        "sub": "Console API Passport",
    }
    # issue a jwt token
    token = jwt.encode(payload, dify_config.SECRET_KEY, algorithm="HS256")
    ic(token)
    # verify a jwt token
    try:
        payload = jwt.decode(token, dify_config.SECRET_KEY, algorithms=["HS256"])
        ic(payload)
    except jwt.exceptions.InvalidSignatureError:
        raise Unauthorized("Invalid token signature.")
    except jwt.exceptions.DecodeError:
        raise Unauthorized("Invalid token.")
    except jwt.exceptions.ExpiredSignatureError:
        raise Unauthorized("Token has expired.")
