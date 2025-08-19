from typing import Literal, Union

from flask import request
from flask_login import current_user  # type: ignore
from flask_restful import Resource, marshal_with  # type: ignore
from werkzeug.exceptions import Forbidden

import services
from configs import dify_config
from constants import DOCUMENT_EXTENSIONS
from controllers.common.errors import FilenameNotExistsError
from controllers.console.wraps import (
    account_initialization_required,
    cloud_edition_billing_resource_check,
    setup_required,
)
from fields.file_fields import file_fields, upload_config_fields
from libs.login import login_required
from services.file_service import FileService
from .error import (
    FileTooLargeError,
    NoFileUploadedError,
    TooManyFilesError,
    UnsupportedFileTypeError,
)

PREVIEW_WORDS_LIMIT = 3000


class FileApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(upload_config_fields)
    def get(self):
        return {
            "file_size_limit": dify_config.UPLOAD_FILE_SIZE_LIMIT,
            "batch_count_limit": dify_config.UPLOAD_FILE_BATCH_LIMIT,
            "image_file_size_limit": dify_config.UPLOAD_IMAGE_FILE_SIZE_LIMIT,
            "video_file_size_limit": dify_config.UPLOAD_VIDEO_FILE_SIZE_LIMIT,
            "audio_file_size_limit": dify_config.UPLOAD_AUDIO_FILE_SIZE_LIMIT,
            "workflow_file_upload_limit": dify_config.WORKFLOW_FILE_UPLOAD_LIMIT,
        }, 200

    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(file_fields)
    @cloud_edition_billing_resource_check("documents")
    def post(self):
        """
        处理文件上传请求

        该方法处理POST请求中的文件上传，支持从表单数据中获取文件和来源信息，
        并根据用户权限和文件类型进行相应的验证和处理。

        Returns:
            tuple: 包含上传文件信息和HTTP状态码201的元组

        Raises:
            NoFileUploadedError: 当请求中没有文件时抛出
            TooManyFilesError: 当上传文件数量超过1个时抛出
            FilenameNotExistsError: 当文件名不存在时抛出
            Forbidden: 当用户没有数据集编辑权限但尝试上传到数据集时抛出
            FileTooLargeError: 当文件大小超过限制时抛出
            UnsupportedFileTypeError: 当文件类型不被支持时抛出
        """
        file = request.files["file"]
        source_str = request.form.get("source")
        source: Union[Literal["datasets"], None] = (
            "datasets" if source_str == "datasets" else None
        )

        # 验证文件上传的基本要求
        if "file" not in request.files:
            raise NoFileUploadedError()

        if len(request.files) > 1:
            raise TooManyFilesError()

        if not file.filename:
            raise FilenameNotExistsError

        # 检查用户权限，如果来源是数据集但用户不是数据集编辑者则拒绝访问
        if source == "datasets" and not current_user.is_dataset_editor:
            raise Forbidden()

        # 验证来源参数，如果不是有效值则设为None
        if source not in ("datasets", None):
            source = None

        # 处理文件上传逻辑
        try:
            upload_file = FileService.upload_file(
                filename=file.filename,
                content=file.read(),
                mimetype=file.mimetype,
                user=current_user,
                source=source,
            )
        except services.errors.file.FileTooLargeError as file_too_large_error:
            raise FileTooLargeError(file_too_large_error.description)
        except services.errors.file.UnsupportedFileTypeError:
            raise UnsupportedFileTypeError()

        return upload_file, 201


class FilePreviewApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    def get(self, file_id):
        file_id = str(file_id)
        text = FileService.get_file_preview(file_id)
        return {"content": text}


class FileSupportTypeApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        return {"allowed_extensions": DOCUMENT_EXTENSIONS}
