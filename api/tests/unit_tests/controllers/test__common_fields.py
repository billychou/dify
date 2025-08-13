#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test__common_fields.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/8/13
Copyright: @三分地技术有限公司
"""
from flask_restful import fields

from controllers.common.fields import parameters_fields


def test_controller_common_fields_parameters_fields():
    """
    fields
    """
    assert parameters_fields["opening_statement"] == fields.String
