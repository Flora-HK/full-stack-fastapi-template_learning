# pyright: reportAny=false
import uuid

# UTC 是带时区信息的时区对象（Python 3.11+ 推荐用法，替代 pytz.UTC）
# datetime.now(UTC) 生成带时区的时间，存到 PostgreSQL 的 timestamptz 字段不会丢时区
from datetime import UTC, datetime

# pydantic 内置的邮箱字符串类型，会自动校验格式
from pydantic import EmailStr

# SQLAlchemy 列类型：DateTime(timezone=True) 表示带时区的 datetime，对应 PostgreSQL 的 timestamptz
from sqlalchemy import DateTime

# SQLModel = SQLAlchemy + Pydantic，类既可当 SQLAlchemy ORM 模型，也可当 Pydantic 模型做 API 校验
# Field        字段描述符，对应 SQLAlchemy Column + Pydantic Field 的合并能力
# Relationship 声明 ORM 关系（一对多 / 多对一），可自动做 JOIN
# SQLModel     所有模型类的基类
from sqlmodel import Field, Relationship, SQLModel


# 生成带时区信息的 UTC 当前时间，作为 ORM 默认值
def get_datetime_utc() -> datetime:
    return datetime.now(UTC)


# Shared properties
# 共享字段：用户模型的所有变体（Create / Update / DB / Public）都复用这些字段
class UserBase(SQLModel):
    # unique=True 邮箱唯一；index=True 自动建索引，提升按邮箱查询速度
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    # 是否启用账户，管理员可停用某个用户而不删除
    is_active: bool = True
    # 是否是超级管理员，影响权限装饰器（Depends(get_current_superuser)）
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
# 管理员创建用户时的请求体，比 UserBase 多了 password（明文）
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


# Properties to receive via API on register (open to public)
# 公开注册接口的请求体（不复用 UserBase 是为了把暴露面收窄到最小）
class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
# 管理员更新任意用户时的请求体，所有字段可选（PATCH 风格）
class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)


# 用户自己更新个人信息时能改的字段（不允许改 is_active / is_superuser）
class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


# 用户改密码时的请求体，需要提供旧密码做校验
class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
# table=True 才会真正映射到数据库表（默认 SQLModel 不映射，只当 Pydantic 模型）
# 将“类”映射成“表”，其中用Field()定义的属性映射成表中的列，用Relationship()定义的属性映射成表中的关系
# 表名默认取类名小写 -> "user"
class User(UserBase, table=True):
    # default_factory 让每次新建行自动生成一个 UUID v4
    # primary_key=True 设为主键
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # 数据库存的是哈希后的密码，永远不要存明文
    hashed_password: str
    # sa_type 强制使用 SQLAlchemy 的 DateTime(timezone=True)，对应 PostgreSQL 的 timestamptz
    # 不写 sa_type 时 SQLModel 推断成 timestamp without time zone，跨时区会出错
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    # 反向关系：一个用户拥有多个 Item
    # back_populates="owner" 指向 Item.owner，构成双向关系
    # cascade_delete=True：当用户被删除时，SQLAlchemy 层面级联删除关联的 items
    items: list[Item] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
# 返回给前端的用户信息（不含密码等敏感字段），id 必现
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


# 列表接口的响应包装：data + count，前端做分页用
class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
# Item 的共享字段
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
# 创建 Item 的请求体，直接复用 ItemBase
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
# 更新 Item 的请求体，所有字段可选（PATCH 风格）
class ItemUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Database model, database table inferred from class name
# Item 表，对应数据库表 "item"
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    # 外键，指向 user.id（SQLAlchemy 里表名是类名小写 -> "user"）
    # nullable=False：每个 Item 必须有归属用户
    # ondelete="CASCADE"：数据库层面级联删除（用户被删 -> 关联 item 也删）
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    # 反向指向 User.items；这里不写 cascade_delete 是因为 owner_id 已经做了数据库级联
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
# 返回给前端的 Item 信息
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


# Item 列表接口的响应包装
class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
# 通用消息体（用于"操作成功 / 失败"等简单响应）
class Message(SQLModel):
    message: str


# JSON payload containing access token
# 登录接口返回的 access token 响应体
class Token(SQLModel):
    access_token: str
    # token 类型固定 bearer，符合 OAuth2 规范
    token_type: str = "bearer"


# Contents of JWT token
# 解析后的 JWT payload：sub 是用户 id（JWT 标准 claim）
class TokenPayload(SQLModel):
    sub: str | None = None


# 密码重置接口的请求体：先用 token 校验，再用新密码更新
class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
