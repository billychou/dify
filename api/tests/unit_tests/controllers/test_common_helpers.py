#!/usr/bin/env python3
"""
File: test_common_helpers.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/8/13
Copyright: @三分地技术有限公司
"""
import httpx

from controllers.common.helpers import FileInfo, guess_file_info_from_response


def test__file_info():
    file_info = FileInfo(
        filename="test.txt", extension="txt", mimetype="text/plain", size=1024
    )
    assert file_info.filename == "test.txt"


def test__httpx_request():
    """
    httpx
    """
    url = "https://api.ipstack.com/134.201.250.155?access_key=fe80f020010028ab9f810d89d94905be"
    response = httpx.get(url)
    print(response.text)


def test__guess_file_info_from_response():
    url = "https://www.gnu.org/software/hello/manual/hello.pdf"
    response = httpx.get(url)
    file_info = guess_file_info_from_response(response)
    print(file_info)


def test__get_parameters_from_feature_dict():
    """
    get parmeters from feature dict
    """
    from controllers.common.helpers import get_parameters_from_feature_dict
    from collections.abc import Mapping
    from typing import Any
    from typing import List

    features_dict: Mapping[str, Any] = {
        "name": "test",
        "description": "test",
        "parameters": [
            {
                "name": "test",
                "description": "test",
                "type": "string",
                "required": True,
                "default": "test",
            }
        ],
    }

    user_input_form: List[dict[str, Any]] = [{"name": "test"}]
    ret = get_parameters_from_feature_dict(
        features_dict=features_dict, user_input_form=user_input_form
    )
    print(type(ret))
    print(ret)
