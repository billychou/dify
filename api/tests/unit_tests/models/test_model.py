#!/usr/bin/env python3
"""
File: test_model.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/8/12
Copyright: @三分地技术有限公司
"""
from models.model import AppMode


def test_app_mode_value_of():
    assert AppMode.value_of("channel") == AppMode.CHANNEL
    assert AppMode.CHANNEL.value == "channel"
    assert AppMode.CHANNEL == "channel"
