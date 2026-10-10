# FastAPI 项目 - 前端

> **本文件说明**：本文是 `frontend/README.md` 的中文翻译版，对应上游文件 `frontend/README.md`，翻译日期 **2026-10-05**。
> 上游仓库持续更新，若日后英文原文有改动，本文可能滞后失效，请以英文原文为准。
> 本文件为新增文件，不修改上游任何内容。

前端使用 [Vite](https://vitejs.dev/)、[React](https://react.dev/)、[TypeScript](https://www.typescriptlang.org/)、[TanStack Query](https://tanstack.com/query)、[TanStack Router](https://tanstack.com/router)、[Tailwind CSS](https://tailwindcss.com) 与 [shadcn/ui](https://ui.shadcn.com/) 构建。

## 环境要求

- [Bun](https://bun.sh/)

## 快速开始

在项目根目录下安装依赖并启动前端开发服务器：

```bash
bun install
bun run dev
```

然后在浏览器中打开 <http://localhost:5173/>。

在 `backend` 目录下运行 `uv run bash scripts/prestart.sh` 与 `uv run fastapi dev`，并确保 PostgreSQL 已在 Docker Compose 中运行。完整步骤见 [../development.md](../development.md)。

若想让 FastAPI 提供前端服务，请在 `frontend` 目录下运行 `bun run build`，然后打开 `http://localhost:8000`。

其他可用命令请查看 `frontend/package.json`。

## 移除前端

如果你要开发纯 API 应用并想移除前端，可以很轻松地做到：

* 删除 `./frontend` 目录。

* 在 `backend/app/main.py` 文件中，删除 `app.frontend()` 调用。

* 在 `backend/Dockerfile` 文件中，删除前端构建阶段以及 `COPY --from=frontend-build` 指令。

* 在 `compose.override.yml` 文件中，删除 `playwright` 服务。

* 在 `.github/workflows/deploy.yml` 文件中，删除 **Set up Bun**、**Install frontend dependencies** 与 **Build frontend** 这几个步骤。

* 在 `.fastapicloudignore` 文件中，删除 `!backend/app/frontend/` 这一项。

完成，你现在拥有一个纯 API 应用。🤓

## 生成客户端

### 自动方式

* 在项目根目录下运行脚本：

```bash
bash ./scripts/generate-client.sh
```

* 提交这些改动。

### 手动方式

* 确保后端正在运行。

* 从 `http://localhost:8000/api/v1/openapi.json` 下载 OpenAPI JSON 文件，并复制为 `frontend` 目录根下的新文件 `openapi.json`。

* 生成前端客户端：

```bash
bun run generate-client
```

* 提交这些改动。

只要后端改动影响到 OpenAPI schema，就需要重新生成客户端。

## 使用远程 API

默认情况下，构建后的前端与 FastAPI 应用使用同一源（same origin）。如果你在运行 Vite 开发服务器时想使用远程 API，可以把环境变量 `VITE_API_URL` 设为该远程 API 的 URL。例如，可以在 `frontend/.env` 文件中设置：

```env
VITE_API_URL=https://my-domain.example.com
```

这样运行前端时，它会使用该 URL 作为 API 的 base URL。

## 代码结构

前端代码结构如下：

* `frontend/src` - 前端主要代码。
* `frontend/public` - 静态资源。
* `frontend/src/client` - 生成的 OpenAPI 客户端。
* `frontend/src/components` - 前端组件，包含 `frontend/src/components/ui` 中的 shadcn/ui 组件。
* `frontend/src/hooks` - 自定义 hooks。
* `frontend/src/lib` - 前端共享工具函数。
* `frontend/src/routes` - 前端路由与页面。

## 使用 Playwright 进行端到端测试

前端包含使用 Playwright 编写的初始端到端测试。要运行测试，你需要先让 Docker Compose 服务栈处于运行状态。用以下命令启动服务栈：

```bash
docker compose run --rm backend bash scripts/prestart.sh
docker compose up -d --wait backend
```

然后用以下命令运行测试：

```bash
bunx playwright test
```

你也可以用 UI 模式运行测试，直接看到浏览器并与之交互：

```bash
bunx playwright test --ui
```

要停止并移除 Docker Compose 服务栈、清理测试产生的数据，请使用：

```bash
docker compose down -v
```

要更新测试，请进入 tests 目录，按需修改现有测试文件或添加新文件。

有关编写与运行 Playwright 测试的更多信息，请参考官方 [Playwright 文档](https://playwright.dev/docs/intro)。
