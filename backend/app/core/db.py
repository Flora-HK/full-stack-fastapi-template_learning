# pyright: reportMissingTypeStubs=false
from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate

# pool_pre_ping=True 每次从连接池取连接前先发一条"探活"语句（默认 SELECT 1）
# 防止数据库重启后连接池里残留死连接导致请求失败
engine = create_engine(str(settings.DATABASE_URL), pool_pre_ping=True)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28
# 重要：必须先 import app.models（让所有 ORM 类完成注册），再去操作 SQLModel.metadata
# 否则 Relationship / ForeignKey 等跨表引用可能找不到目标表，导致启动时元数据初始化报错


# 初始化数据库：当前只做"创建首个超级管理员"，
# 表结构由 Alembic 迁移脚本负责（prestart.sh -> alembic upgrade head）
def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    # 按邮箱查询是否已存在首个超级管理员，避免重复创建
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        # 若不存在，用 .env 里配置的用户名密码创建一个
        # is_superuser=True 直接赋予超级管理员权限
        # 密码会在 crud.create_user 内部做哈希，不会以明文入库
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
