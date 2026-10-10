# FastAPI 项目 - 开发

> **本文件说明**：本文是 `development.md` 的中文翻译版，对应上游文件 `development.md`，翻译日期 **2026-10-05**。
> 上游仓库持续更新，若日后英文原文有改动，本文可能滞后失效，请以英文原文为准。
> 本文件为新增文件，不修改上游任何内容。

## 本地开发

本地开发时，用 Docker Compose 运行 PostgreSQL 与 Mailpit，并在本地运行 FastAPI 与 Vite 开发服务器。

启动支撑服务：

```bash
docker compose up -d db mailpit
```

然后，在 `backend` 目录下安装依赖并准备数据库：

```bash
uv sync
uv run bash scripts/prestart.sh
```

启动 FastAPI 开发服务器：

```bash
uv run fastapi dev
```

在另一个终端中，从项目根目录安装前端依赖并启动 Vite 开发服务器：

```bash
bun install
bun run dev
```

现在你可以打开以下 URL：

前端开发服务器：<http://localhost:5173>

后端 API：<http://localhost:8000>

自动生成的交互式 API 文档（Swagger UI）：<http://localhost:8000/docs>

Mailpit：<http://localhost:8025>

前端开发服务器使用 `http://localhost:8000` 上的后端，这在 `frontend/.env` 中配置。

### 由 FastAPI 提供前端服务

在 `frontend` 目录下构建前端：

```bash
bun run build
```

构建产物会写入 `backend/app/frontend`，并由 FastAPI 在 <http://localhost:8000> 提供。每次修改前端后都需要重新构建。

## 使用 Docker Compose 运行全栈

要在 Docker Compose 中运行后端与已构建的前端：

```bash
docker compose run --rm backend bash scripts/prestart.sh
docker compose watch
```

现在你可以打开以下 URL：

应用（前端与 API 均由 FastAPI 提供）：<http://localhost:8000>

自动生成的交互式 API 文档（Swagger UI）：<http://localhost:8000/docs>

Adminer，数据库 Web 管理界面：<http://localhost:8080>

Traefik UI，用于查看代理如何处理路由：<http://localhost:8090>

Mailpit：<http://localhost:8025>

在启动 Compose 后端之前，请先停止本地正在运行的 FastAPI 服务器，因为两者都使用 `8000` 端口。

**注意**：首次启动整套服务时，所有服务就绪可能需要一分钟。要监控状态，可以使用 `docker compose logs`，或针对后端服务使用 `docker compose logs backend`。

## Mailpit

[Mailpit](https://mailpit.axllent.org) 会捕获本地开发期间发送的邮件，而不是真正投递出去。本地后端通过 `localhost:1025` 连接它，而 Compose 中的后端则连接 `mailpit` 服务。被捕获的邮件可在 <http://localhost:8025> 查看。

## Docker Compose 文件与环境变量

主文件 `compose.yml` 包含整套服务共享的配置。Docker Compose 会自动加载它。

`compose.override.yml` 文件追加本地开发设置，例如把源码挂载为卷。Docker Compose 也会自动加载它，并把它叠加在 `compose.yml` 之上。

`compose.deploy.yml` 文件包含部署专用设置，包括 HTTPS 与自动证书处理。部署应用时，需要把它与 `compose.yml` 显式组合使用。

后端从 `.env` 文件读取本地设置。Docker Compose 也使用它做变量插值，并把各容器所需的设置传进去。

修改变量后，请确保重启整套服务：

```bash
docker compose watch
```

## `.env` 文件

被 Git 跟踪的 `.env` 文件包含本地开发默认值、密码以及其他配置。其中主机名使用 `localhost`，面向的是运行在你机器上的进程。Docker Compose 会把数据库、SMTP 服务器等主机名覆盖为对应的 Compose 服务名。

不要在 `.env` 中存放部署密钥。请按 [FastAPI Cloud 部署指南](./deployment.md) 或 [Docker Compose 部署指南](./deployment-docker-compose.md) 中的说明进行配置。

## Pre-commit 钩子与代码检查

项目使用 [prek](https://prek.j178.dev/)——[pre-commit](https://pre-commit.com/) 的现代替代品——进行代码检查与格式化。

你可以在项目根目录找到配置文件 `.pre-commit-config.yaml`。

### 安装 `prek` 以自动运行

`prek` 已经是项目依赖的一部分。

从项目根目录安装 Git 钩子，让 `prek` 在每次提交前自动运行：

```bash
uv run prek install -f
```

`-f` 参数会强制安装，以防之前已经装过 `pre-commit` 钩子。

现在每当你尝试提交时，例如使用：

```bash
git commit
```

`prek` 会检查并格式化你即将提交的代码。如果它修改了任何文件，请把这些文件重新加入 Git 后再提交。

### 手动运行 `prek`

你也可以从项目根目录对所有文件手动运行 `prek`：

```bash
uv run prek run --all-files
```
