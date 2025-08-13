import os
from textwrap import dedent

import pytest
from flask import Flask
from yarl import URL

from configs.app_config import DifyConfig

EXAMPLE_ENV_FILENAME = ".env"


@pytest.fixture
def example_env_file(tmp_path, monkeypatch) -> str:
    """
    创建一个示例环境变量文件的pytest fixture

    该fixture会在临时目录中创建一个包含预定义环境变量的.env文件，
    主要用于测试需要读取环境配置的功能

    参数:
        tmp_path: pytest内置fixture，提供临时目录路径, pathlib.Path对象
        monkeypatch: pytest内置fixture，用于临时修改环境或路径

    返回:
        str: 创建的环境变量文件的完整路径
    """
    # 切换当前工作目录到临时目录
    monkeypatch.chdir(tmp_path)

    # 在临时目录中创建环境变量文件
    file_path = tmp_path.joinpath(EXAMPLE_ENV_FILENAME)
    file_path.write_text(
        dedent(
            """
        CONSOLE_API_URL=https://example.com
        CONSOLE_WEB_URL=https://example.com
        HTTP_REQUEST_MAX_WRITE_TIMEOUT=30
        """
        )
    )

    # 返回创建的文件路径
    return str(file_path)


def test_dify_config_undefined_entry(example_env_file):
    """
    测试Dify配置中未定义条目的访问行为。

    该测试验证当尝试访问未在AppSettings中明确定义的配置项时，
    系统是否能正确抛出TypeError异常。

    参数:
        example_env_file: 环境变量文件路径，用于加载测试配置

    返回值:
        无返回值，通过异常抛出和断言验证测试结果
    """
    # NOTE: See https://github.com/microsoft/pylance-release/issues/6099 for more details about this type error.
    # 使用pydantic-settings加载dotenv文件配置
    config = DifyConfig(_env_file=example_env_file)

    # 测试访问未在应用设置中定义的配置项
    with pytest.raises(TypeError):
        # TypeError: 'AppSettings' object is not subscriptable
        assert config["LOG_LEVEL"] == "INFO"
        # assert config["FILES_URL"] == "https://example.com"
        # assert config.FILES_URL == "http://127.0.0.1:5001"


# NOTE: If there is a `.env` file in your Workspace, this test might not succeed as expected.
# This is due to `pymilvus` loading all the variables from the `.env` file into `os.environ`.
def test_dify_config(example_env_file):
    """
    测试Dify配置加载功能

    该函数用于验证Dify配置类能够正确加载环境变量文件，并验证各种配置项的默认值
    和加载值是否符合预期。

    参数:
        example_env_file: 环境变量文件路径，用于加载测试配置

    返回值:
        无返回值，通过断言验证配置项的正确性
    """
    # 清空系统环境变量，确保测试环境的纯净性
    os.environ.clear()

    # 使用pydantic-settings加载指定的环境变量文件
    config = DifyConfig(_env_file=example_env_file)

    # 验证常量值配置项
    assert config.COMMIT_SHA == ""

    # 验证默认值配置项
    assert config.EDITION == "SELF_HOSTED"
    assert config.API_COMPRESSION_ENABLED is False
    assert config.SENTRY_TRACES_SAMPLE_RATE == 1.0

    # 验证带注解的默认值字段
    assert config.HTTP_REQUEST_MAX_READ_TIMEOUT == 60

    # 验证带注解的已配置值字段
    assert config.HTTP_REQUEST_MAX_WRITE_TIMEOUT == 30

    assert config.WORKFLOW_PARALLEL_DEPTH_LIMIT == 3


# NOTE: If there is a `.env` file in your Workspace, this test might not succeed as expected.
# This is due to `pymilvus` loading all the variables from the `.env` file into `os.environ`.
def test_flask_configs(example_env_file):
    """
    测试 Flask 应用配置加载功能。

    该函数用于验证 Flask 应用是否能正确从环境文件和 Pydantic 配置中加载配置项，
    并检查关键配置项的值是否符合预期。

    参数:
        example_env_file (str): 示例环境变量文件路径，用于模拟环境变量配置。

    返回值:
        无返回值。通过断言验证配置项的正确性。
    """
    flask_app = Flask("app")
    # 清除系统环境变量，确保测试环境干净
    os.environ.clear()
    # 从 Pydantic 配置模型加载配置并应用到 Flask 应用
    flask_app.config.from_mapping(
        DifyConfig(_env_file=example_env_file).model_dump()
    )  # pyright: ignore
    config = flask_app.config

    # 验证从 Pydantic 配置模型中读取的默认配置项
    assert config["LOG_LEVEL"] == "INFO"
    assert config["COMMIT_SHA"] == ""
    assert config["EDITION"] == "SELF_HOSTED"
    assert config["API_COMPRESSION_ENABLED"] is False
    assert config["SENTRY_TRACES_SAMPLE_RATE"] == 1.0

    # 验证从环境变量文件中加载的配置项
    assert config["CONSOLE_API_URL"] == "https://example.com"
    # 验证别名配置项是否正确回退并赋值
    assert config["FILES_URL"] == "https://example.com"

    # 验证数据库相关配置项
    assert (
        config["SQLALCHEMY_DATABASE_URI"]
        == "postgresql://postgres:@localhost:5432/dify"
    )
    assert config["SQLALCHEMY_ENGINE_OPTIONS"] == {
        "connect_args": {
            "options": "-c timezone=UTC",
        },
        "max_overflow": 10,
        "pool_pre_ping": False,
        "pool_recycle": 3600,
        "pool_size": 30,
    }

    # 验证控制台和跨域相关配置项
    assert config["CONSOLE_WEB_URL"] == "https://example.com"
    assert config["CONSOLE_CORS_ALLOW_ORIGINS"] == ["https://example.com"]
    assert config["WEB_API_CORS_ALLOW_ORIGINS"] == ["*"]

    # 验证代码执行服务的端点配置
    assert str(config["CODE_EXECUTION_ENDPOINT"]) == "http://sandbox:8194/"
    assert (
        str(URL(str(config["CODE_EXECUTION_ENDPOINT"])) / "v1")
        == "http://sandbox:8194/v1"
    )
