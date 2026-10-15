# warnings 发出、控制和过滤'警告信息'
# Literal 字符串字面量类型，将某个参数/变量的值锁定到几个具体的字面量值中
# Self 用于在方法返回值里引用"当前实例自身的类型"（Python 3.11+ 也可直接用 typing.Self）
import warnings
from typing import Literal, Self

# 将类型注解变成强制规则，不符合条件即报错，类型检验
# EmailStr     pydantic 内置邮箱字符串类型，会自动校验邮箱格式
# HttpUrl      pydantic 内置 HTTP URL 类型，自动校验 URL 合法性
# PostgresDsn  pydantic 内置 PostgreSQL DSN 类型，自动校验连接串格式
# computed_field 把 @property 标记为字段，让它能出现在 .model_dump() / API 响应中
# field_validator 字段级校验器，可对单个字段进行加工或校验
# model_validator  模型级校验器，可跨字段加工或校验
from pydantic import (
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    field_validator,
    model_validator,
)

# BaseSettings 继承自 BaseModel，启动时自动从 .env / 环境变量读取同名配置
# SettingsConfigDict 用来精细控制 BaseSettings 的行为
from pydantic_settings import BaseSettings, SettingsConfigDict


# BaseSettings 是 BaseModel + 自动读取 .env / 环境变量
# Settings 类是项目全局配置的唯一来源，所有模块都通过 settings.xxx 访问配置
class Settings(BaseSettings):
    # SettingsConfigDict 控制 BaseSettings 的读取行为
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        # 从 backend 目录的上一级（项目根）读取 .env
        env_file="../.env",
        # 环境变量值为空字符串时忽略，避免把空串当作有效值覆盖默认值
        env_ignore_empty=True,
        # .env 中多余的字段不抛错，保持向前兼容
        extra="ignore",
    )
    # 所有 API 路由的前缀，main.py 中挂载路由时使用
    API_V1_STR: str = "/api/v1"
    # 用于签发 / 校验 JWT 等加密操作的密钥，部署前必须替换为真随机长串
    SECRET_KEY: str
    # 60 minutes * 24 hours * 8 days = 8 days
    # JWT access token 的过期时间（分钟）
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # 前端开发服务器地址，用于生成邮件里的重置链接等
    FRONTEND_HOST: str = "http://localhost:5173"
    # 当前运行环境：development 模式下放宽部分安全校验（如默认密钥只警告、不抛错）
    # 用 Literal 把可选值锁定在 "development"，拼错时会立即报错
    FASTAPI_ENV: Literal["development"] | None = None

    # 项目名称，用于邮件 / 日志 / Sentry 等场景
    PROJECT_NAME: str
    # Sentry 错误监控接入地址，未配置则禁用 Sentry
    SENTRY_DSN: HttpUrl | None = None
    # PostgreSQL 数据库连接串（DSN）
    DATABASE_URL: PostgresDsn

    # mode="before" 表示在校验器之前对原始值加工（拿到的是 str，不是已经被校验过的 PostgresDsn）
    # 这里把 postgres:// / postgresql:// 替换为 postgresql+psycopg://
    # SQLAlchemy 2.x 默认驱动改为 psycopg（v3），所以需要显式声明
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _use_psycopg_driver(cls, value: str | PostgresDsn) -> str:
        database_url = str(value)
        for scheme in ("postgres://", "postgresql://"):
            if database_url.startswith(scheme):
                return database_url.replace(scheme, "postgresql+psycopg://", 1)
        return database_url

    # SMTP 是简单邮件传输协议，用于发送邮件（只发不收）
    # 这里配置 SMTP 服务器地址、用户名、密码等，用于发送邮件
    # 未配置则禁用邮件发送（见 emails_enabled）
    # SMTP 是否使用 STARTTLS（一般端口 587）
    SMTP_TLS: bool = True
    # SMTP 是否使用 SSL（实则为TLS，一般端口 465）
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    # SMTP 服务器地址，为空则禁用邮件发送（见 emails_enabled）
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    # 发件人邮箱地址
    EMAILS_FROM_EMAIL: EmailStr | None = None
    # 发件人显示名，未配置时回退到 PROJECT_NAME（见 _set_default_emails_from）
    EMAILS_FROM_NAME: str | None = None

    # model_validator(mode="after") 在所有字段校验完成后整体加工一次
    # 这里给 EMAILS_FROM_NAME 提供"配置缺省时自动用项目名"的回退值
    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    # 密码重置邮件里 token 的有效期（小时）
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    # computed_field 把下面的 @property 也当作普通字段
    # 这样它会出现在模型序列化结果 / OpenAPI 文档里
    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        # 只有 SMTP_HOST 和 EMAILS_FROM_EMAIL 都配置了，才启用邮件功能
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    # 用于在开发模式下接收测试邮件的固定账号
    EMAIL_TEST_USER: EmailStr = "test@example.com"
    # 首次启动时自动创建的超级管理员邮箱
    FIRST_SUPERUSER: EmailStr
    # 首次启动时自动创建的超级管理员密码（会被哈希后再入库）
    FIRST_SUPERUSER_PASSWORD: str

    # 检查某个配置项是否仍是占位符 "changethis"
    # 占位符在开发模式只警告，在生产模式直接抛错，避免带着默认密钥上线
    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.FASTAPI_ENV == "development":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    # 整体启动时强制检查若干关键密钥，避免上线后被默认密钥坑
    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        # SECRET_KEY 必须是真随机长串
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        # PostgresDsn.hosts() 返回连接串里所有主机段（host、port、user、password 等字典）
        # 这里只检查 password 段，避免把整个连接串打出来
        for host in self.DATABASE_URL.hosts():
            self._check_default_secret("DATABASE_URL password", host["password"])
        # 超级管理员密码也得改
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self


# 在模块导入时实例化一次，整个进程复用同一个 settings 对象
# 实例化失败时会抛校验错误（缺字段、生产模式默认密钥、邮箱格式非法等）
settings = Settings()  # type: ignore # ty: ignore[unused-ignore-comment]
