#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_common_errors.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/8/13
Copyright: @三分地技术有限公司
"""
import pytest

from controllers.common.errors import FilenameNotExistsError, RemoteFileUploadError


def test__controllers_common_filename_not_exists_error():
    with pytest.raises(FilenameNotExistsError):
        raise FilenameNotExistsError()


def test__controllers_common_remote_file_upload_error():
    with pytest.raises(RemoteFileUploadError):
        raise RemoteFileUploadError()
