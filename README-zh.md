# full-stack-fastapi-template — 学习说明（中文指南）

> 仓库：https://github.com/fastapi/full-stack-fastapi-template （FastAPI 官方出品的全栈生产模板）
> 本文件是我自己添加的学习笔记，不属于上游仓库内容，不会影响上游更新（`git pull` 时会保留）。

## 零、版本与本机环境（2026-09-10 核对）

- **克隆状态**：完整克隆（非浅克隆），分支 `master`，共 1509 次提交，HEAD `cb740b6`（2026-09-01）。
- **工作区**：干净，未跟踪文件只有本文件 `README-zh.md`。仓库内容完整（backend 57 / frontend 119 / packages 11 个文件）。
- **后端要求 Python `>=3.14,<4.0`**（见 `backend/pyproject.toml`）—— 本机是 **Python 3.14.3，满足要求**。
- **本机已装**：Python 3.14.3、Docker 29.6.1、Node v24.19.0 / npm 11.17.0。
- **本机缺**：`uv`（后端依赖管理，官方新流程，需先装）、`bun`（前端依赖管理，需先装；也可退回 npm）。
- **主要依赖**：FastAPI ≥0.141.1、SQLModel ≥0.0.39、Alembic ≥1.19.1、psycopg3（PostgreSQL 驱动）、pwdlib[argon2,bcrypt]（密码哈希）、PyJWT（Token）。

## 一、为什么先学它

我当前的缺口是"Web 后端零实战"。这个模板一次补齐计划中的所有后端知识点，而且是**行业认可的写法**：

- FastAPI + SQLModel/SQLAlchemy + PostgreSQL + Alembic 迁移
- Pydantic 校验 + Pydantic-Settings 配置管理
- JWT/OAuth2 登录鉴权、密码加密
- 分层结构：路由 → CRUD → Model 清晰分离
- pytest 测试、GitHub Actions / CI 配置
- Docker / Docker Compose 一键起多服务（后端 + 数据库 + 前端）
- 自带前端（React + Vite + TypeScript），前后端可一起跑通

与其从零手写一个"烂大街学生管理系统"，不如**精读它 → 改造成自己的项目**，质量高一个量级。

## 二、仓库结构速览（当前版本为 uv 管理）

```
full-stack-fastapi-template/
├── backend/                      # FastAPI 后端
│   └── app/
│       ├── main.py               # 应用入口
│       ├── api/                  # 路由层
│       │   ├── main.py           # 路由汇总
│       │   ├── deps.py           # 依赖注入（获取当前用户/数据库会话）
│       │   └── routes/           # 各业务路由（items、users、login 等）
│       ├── core/                 # 核心
│       │   ├── config.py         # 环境配置（.env → Settings）
│       │   ├── db.py             # 数据库引擎/会话
│       │   └── security.py       # 密码哈希、JWT
│       ├── models.py             # ⭐ 表模型 + Pydantic Schema 都在这里（注意：没有单独的 schemas.py）
│       ├── crud.py               # 通用 CRUD 封装
│       ├── utils.py              # 邮件渲染/发送、密码重置 Token 的签发与校验
│       ├── initial_data.py       # 初始化种子数据
│       ├── email-templates/      # 邮件 HTML 模板（Jinja2）
│       └── alembic/              # 数据库迁移
├── backend/tests/                # pytest 测试（api/routes/、crud/、utils/ 测试构造器）
├── frontend/                     # React + Vite + TS 前端（可选学）
├── packages/react-email/         # 邮件模板（可选学）
├── compose.yml                   # Docker Compose 编排
├── pyproject.toml / uv.lock      # Python 依赖（uv）
├── bun.lock / package.json       # 前端依赖
└── development.md                # 官方开发文档（第一步先读它）
```

## 三、怎么跑起来（按顺序）

1. 安装 **Docker Desktop**（Windows 需 WSL2 后端）。
2. 读仓库根目录 `development.md` 和 `README.md`，两者是官方权威步骤。
3. 典型流程（以官方文档为准）：
   ```bash
   cd full-stack-fastapi-template
   # 复制环境变量文件（模板一般自带 .env 示例，看官方说明）
   docker compose up -d --build        # 起后端 + PostgreSQL 等
   docker compose ps                   # 查看服务状态
   ```
4. 后端交互式文档一般位于 `http://localhost:8000/docs`（具体端口以 .env/compose 为准）。
5. 不装 Docker、只用本机 Python 跑后端也是可行的，但数据库迁移/环境会麻烦一些，**建议第一次就按 Docker 走**，这本身就在练 Docker。

## 四、精读路线（建议 5 步，每天 1-2 步）

1. **入口与配置**：`main.py` → `core/config.py`，搞懂 Settings 怎么读 `.env`。
2. **数据层**：`models.py` + `core/db.py` + `alembic/`，理解"模型 ↔ 表 ↔ 迁移"；对照你学习计划里的 SQLAlchemy 笔记。
3. **路由与依赖**：`api/routes/` + `api/deps.py`，看一个完整业务（如 items）从路由 → deps 取当前用户 → crud → 返回 schema 的整条链路。
4. **安全**：`core/security.py` 的 JWT 签发/校验，与登录路由对照，这是面试高频。
5. **测试**：`backend/tests/` 看 pytest 怎么写，理解 TestClient 和依赖覆盖。

读的时候随手给每个目录写一句话总结进你自己的笔记，最后能**不看代码画出一张分层调用图**就算过关。

## 五、复现任务（真正的产出）

学完一轮后，新建你自己的项目（不要在这个目录里写，建议复制一份或另建仓库），例如"课程作业/成绩管理系统"：

- 按模板目录结构从零搭骨架（不强求一模一样，但分层要清晰）
- 手写 5-8 个 CRUD 端点 + 登录鉴权
- 加一次 Alembic 迁移（如给表加字段）
- 写 3-5 个 pytest 用例并跑绿
- Docker Compose 一键起，截图存证

## 六、延伸 Ideas（差异化加分，任选 1-2 个）

- 给热点查询接口加 **Redis 缓存**（相同请求直接返回，记录耗时对比）
- 加 **slowapi 接口限流**
- 加 **操作日志中间件**（记录每个请求的耗时/路径到文件或数据库）
- 加**文件上传 + 静态资源服务**
- 加 **RBAC 角色权限**（如 admin/teacher/student）
- 部署到一台云服务器 / FastAPI Cloud，附上线链接

## 七、简历与面试

简历可写（示例框架，按你实际改动填）：

```
XX管理系统（基于 FastAPI 全栈模板重构）
- 使用 FastAPI + SQLModel + PostgreSQL + Docker Compose 实现前后端分离管理后台
- 实现 JWT 鉴权、XX 业务 CRUD、Alembic 数据迁移、pytest 接口测试
- 延伸：为热点查询引入 Redis 缓存，平均响应从 XXms 降至 XXms（附数据）
```

**红线**：不要只写"我用过模板"就完事——面试官一定会问"JWT 怎么校验的？Docker compose 里网络怎么配的？为什么用 SQLModel 不用原生 SQL？"，答不上来反而扣分。复现时务必亲手写过一遍。

## 八、Windows 常见坑

- Docker Desktop 起不来 → 确认开启 WSL2 + 虚拟化；必要时 `docker desktop` 重启。
- 端口冲突 → 改 `.env`/compose 里映射端口后 `docker compose up -d`。
- 数据库连不上 → 确认容器内数据库名/用户/密码与 `.env` 一致。
- 国内拉镜像慢 → 给 Docker 配国内镜像源，或耐心等待。
