# 1. 标准库-Pathlib导入Path模块，用于处理文件路径
from pathlib import Path

# 2. 第三方库（通过pip安装的外部包）。引入Sentry的 python SDK，用于错误追踪；引入FastAPi框架的核心类； # 引入FastAPI的路由类，用于自定义一个继承自APIRoute的路由类；# 引入跨域资源共享（CORS）中间件
import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

# 3. 自定义模块。引入自定义的路由；引入自定义的配置
from app.api.main import api_router
from app.core.config import settings

FRONTEND_DIR = Path(__file__).parent / "frontend"

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}" # 自定义路由ID生成函数，并将其传递给fastapi的官方内置函数ID生成器'generate_unique_id_function'


if settings.SENTRY_DSN and settings.FASTAPI_ENV != "development":
    '''
    该段代码的作用是，如果配置文件中定义了sentry的DSN，并且当前环境不是开发环境，那么就初始化sentry，用于错误追踪。
    '''
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True) # 'enable_tracing=True'表示启用性能/分布式追踪，不只记报错；'dsn(str)'表示数据源名称，是SDK的核心参数，告诉SDK将事件发送到哪个Sentry项目中。

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    # 'generate_unique_id_function'是官方内置的给路由生成operationId的函数，可以向其传入自定义的路由ID生成函数，在生成OpenAPI时，会自动调用该函数，遍历app.routes，对每个APIRoute实例调用一次，把返回值填进operationId。
    # 生成 OpenAPI 时，会遍历 app.routes，对每个 APIRoute 实例调用一次 generate_unique_id_function(route)，把返回值填进 operationId。
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.frontend("/", directory=FRONTEND_DIR)
