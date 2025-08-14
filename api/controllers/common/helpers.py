import mimetypes
import os
import platform
import re
import urllib.parse
import warnings
from collections.abc import Mapping
from typing import Any
from uuid import uuid4

import httpx

try:
    import magic
except ImportError:
    if platform.system() == "Windows":
        warnings.warn(
            "To use python-magic guess MIMETYPE, you need to run `pip install python-magic-bin`",
            stacklevel=2,
        )
    elif platform.system() == "Darwin":
        warnings.warn(
            "To use python-magic guess MIMETYPE, you need to run `brew install libmagic`",
            stacklevel=2,
        )
    elif platform.system() == "Linux":
        warnings.warn(
            "To use python-magic guess MIMETYPE, you need to run `sudo apt-get install libmagic1`",
            stacklevel=2,
        )
    else:
        warnings.warn(
            "To use python-magic guess MIMETYPE, you need to install `libmagic`",
            stacklevel=2,
        )
    magic = None  # type: ignore

from pydantic import BaseModel

from configs import dify_config


class FileInfo(BaseModel):
    filename: str
    extension: str
    mimetype: str
    size: int


def guess_file_info_from_response(response: httpx.Response):
    """
    从HTTP响应中提取文件信息，包括文件名、扩展名、MIME类型和文件大小。

    参数:
        response (httpx.Response): HTTP响应对象，包含文件下载的相关信息

    返回:
        FileInfo: 包含文件信息的对象，包含以下属性：
            - filename: 文件名
            - extension: 文件扩展名
            - mimetype: MIME类型
            - size: 文件大小（字节）
    """
    url = str(response.url)
    # 尝试从URL中提取文件名
    parsed_url = urllib.parse.urlparse(url)
    # TODO: 为什么不直接使用`response.url.path`解析url_path
    url_path = parsed_url.path
    filename = os.path.basename(url_path)

    # 如果从URL中无法提取文件名，则尝试从Content-Disposition头部获取
    if not filename:
        content_disposition = response.headers.get("Content-Disposition")
        if content_disposition:
            filename_match = re.search(r'filename="?(.+)"?', content_disposition)
            if filename_match:
                filename = filename_match.group(1)

    # 如果仍然没有文件名，则生成一个唯一的文件名
    if not filename:
        unique_name = str(uuid4())
        filename = f"{unique_name}"

    # 首先根据文件名猜测MIME类型，如果失败则根据URL猜测
    mimetype, _ = mimetypes.guess_type(filename)
    if mimetype is None:
        mimetype, _ = mimetypes.guess_type(url)
    if mimetype is None:
        # 如果猜测失败，则使用响应头中的Content-Type
        mimetype = response.headers.get("Content-Type", "application/octet-stream")

    # 如果MIME类型仍然未知或为通用类型，且python-magic可用，则使用magic库进一步检测
    if mimetype == "application/octet-stream" and magic is not None:
        try:
            mimetype = magic.from_buffer(response.content[:1024], mime=True)
        except magic.MagicException:
            pass

    extension = os.path.splitext(filename)[1]

    # 确保文件名包含扩展名
    if not extension:
        extension = mimetypes.guess_extension(mimetype) or ".bin"
        filename = f"{filename}{extension}"

    return FileInfo(
        filename=filename,
        extension=extension,
        mimetype=mimetype,
        size=int(response.headers.get("Content-Length", -1)),
    )


def get_parameters_from_feature_dict(
    *, features_dict: Mapping[str, Any], user_input_form: list[dict[str, Any]]
):
    """
    从特征字典中提取参数配置，用于构建应用的运行时参数。

    :param features_dict: 特征配置字典，包含各种功能开关和配置项
    :param user_input_form: 用户输入表单配置列表
    :return: 包含所有运行时参数的字典，具体包括：
        - opening_statement: 开场白配置
        - suggested_questions: 建议问题列表
        - suggested_questions_after_answer: 回答后建议问题配置
        - speech_to_text: 语音转文字配置
        - text_to_speech: 文字转语音配置
        - retriever_resource: 检索资源配置
        - annotation_reply: 标注回复配置
        - more_like_this: 相似内容推荐配置
        - user_input_form: 用户输入表单配置
        - sensitive_word_avoidance: 敏感词规避配置
        - file_upload: 文件上传配置
        - system_parameters: 系统参数配置（各类文件大小限制）
    """
    return {
        "opening_statement": features_dict.get("opening_statement"),
        "suggested_questions": features_dict.get("suggested_questions", []),
        "suggested_questions_after_answer": features_dict.get(
            "suggested_questions_after_answer", {"enabled": False}
        ),
        "speech_to_text": features_dict.get("speech_to_text", {"enabled": False}),
        "text_to_speech": features_dict.get("text_to_speech", {"enabled": False}),
        "retriever_resource": features_dict.get(
            "retriever_resource", {"enabled": False}
        ),
        "annotation_reply": features_dict.get("annotation_reply", {"enabled": False}),
        "more_like_this": features_dict.get("more_like_this", {"enabled": False}),
        "user_input_form": user_input_form,
        "sensitive_word_avoidance": features_dict.get(
            "sensitive_word_avoidance", {"enabled": False, "type": "", "configs": []}
        ),
        # 文件上传配置，默认支持图片上传，包含数量限制、详细程度和传输方式
        "file_upload": features_dict.get(
            "file_upload",
            {
                "image": {
                    "enabled": False,
                    "number_limits": 3,
                    "detail": "high",
                    "transfer_methods": ["remote_url", "local_file"],
                }
            },
        ),
        # 系统参数配置，包含各类文件上传大小限制
        "system_parameters": {
            "image_file_size_limit": dify_config.UPLOAD_IMAGE_FILE_SIZE_LIMIT,
            "video_file_size_limit": dify_config.UPLOAD_VIDEO_FILE_SIZE_LIMIT,
            "audio_file_size_limit": dify_config.UPLOAD_AUDIO_FILE_SIZE_LIMIT,
            "file_size_limit": dify_config.UPLOAD_FILE_SIZE_LIMIT,
            "workflow_file_upload_limit": dify_config.WORKFLOW_FILE_UPLOAD_LIMIT,
        },
    }
