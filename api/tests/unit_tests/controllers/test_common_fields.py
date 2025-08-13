#!/usr/bin/env python3
"""
File: test_common_fields.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/8/13
Copyright: @三分地技术有限公司
"""
from flask_restful import fields, marshal_with

from controllers.common.fields import parameters_fields


@marshal_with(parameters_fields)
def get_demo():
    return {"opening_statement": "demo"}


def test_controller_common_fields_parameters_fields():
    """
    fields
    """
    a = get_demo()
    assert a["opening_statement"] == "demo"
    assert parameters_fields["opening_statement"] == fields.String
