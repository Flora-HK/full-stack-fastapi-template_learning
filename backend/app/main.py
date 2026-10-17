# pyright: reportMissingTypeStubs=false
# 1. 标准库-Pathlib导入Path模块，用于处理文件路径
from pathlib import Path

# 2. 第三方库（通过pip安装的外部包）。引入Sentry的 python SDK，用于错误追踪；引入FastAPi框架的核心类；
# 引入FastAPI的路由类，用于自定义一个继承自APIRoute的路由类；
# 引入跨域资源共享（CORS）中间件
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
    # 'enable_tracing=True'表示启用性能/分布式追踪，不只记报错；'dsn(str)'表示数据源名称，是SDK的核心参数，告诉SDK将事件发送到哪个Sentry项目中。
    _ = sentry_sdk.init(
        dsn=str(settings.SENTRY_DSN), enable_tracing=True,
    )

app = FastAPI(
    title=settings.PROJECT_NAME,
    # title是FastAPI应用实例的标题，用于生成OpenAPI文档的标题
    openapi_url=f"{settings.API_V1_STR}/openapi.json", # openapi的JSON说明文档应该放在哪个URL，给出用于生成JSON文档的URL
    generate_unique_id_function=custom_generate_unique_id,
    # 'generate_unique_id_function'是官方内置的给路由生成operationId的函数，可以向其传入自定义的路由ID生成函数，在生成OpenAPI时，会自动调用该函数，遍历app.routes，对每个APIRoute实例调用一次，把返回值填进operationId。
    # 生成 OpenAPI 时，会遍历 app.routes，对每个 APIRoute 实例调用一次 generate_unique_id_function(route)，把返回值填进 operationId。
)

# app.add_middleware(中间件类, 若干该中间件的参数)
app.add_middleware(
    CORSMiddleware, # CORS中间件，处理跨域请求（只传类本身，不实例化，由FastAPI内部来new）
    allow_origins=[settings.FRONTEND_HOST], # 允许跨域请求的源，这里只允许来自settings.FRONTEND_HOST的请求
    allow_credentials=True, # 允许请求携带凭证（Cookie、Authorization头、客户端证书）
    allow_methods=["*"], # 允许所有(*)的HTTP方法
    allow_headers=["*"], # 允许请求带所有(*)的自定义头
) # 添加中间件，将CORS中间件注入到FastAPI应用中，允许来自指定源的前端应用进行跨域请求。

app.include_router(api_router, prefix=settings.API_V1_STR) # 挂载模块化路由：'include_router'是fastapi的内置函数，用于将一个路由器添加到app中，'prefix'表示该路由器下的所有路由的公共前缀。
app.frontend("/", directory=FRONTEND_DIR)
