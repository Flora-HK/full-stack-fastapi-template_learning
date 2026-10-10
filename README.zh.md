# 全栈 FastAPI 模板（Full Stack FastAPI Template）

> **本文件说明**：本文是 `README.md` 的中文翻译版，对应上游文件 `README.md`，翻译日期 **2026-10-05**。
> 上游仓库持续更新，若日后 `README.md` 有改动，本文可能滞后失效，请以英文原文为准。
> 本文件为新增文件，不修改上游任何内容；根目录另有 `README-zh.md`，那是学习者自己的笔记，与本文无关。

[![Test Docker Compose](../../actions/workflows/test-docker-compose.yml/badge.svg)](../../actions/workflows/test-docker-compose.yml)
[![Test Backend](../../actions/workflows/test-backend.yml/badge.svg)](../../actions/workflows/test-backend.yml)

## 技术栈与特性

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) 用于 Python 后端 API。
  - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) 用于 Python 中的 SQL 数据库交互（ORM）。
  - 🔍 [Pydantic](https://docs.pydantic.dev) 由 FastAPI 使用，负责数据校验与配置管理。
  - 💾 [PostgreSQL](https://www.postgresql.org) 作为 SQL 数据库。
- 🚀 [React](https://react.dev) 用于前端。
  - 🧩 内置于后端应用中，由 FastAPI 在同一域名下与 API 一起对外提供服务。
  - 💃 使用 TypeScript、hooks、[Vite](https://vitejs.dev) 以及现代前端技术栈的其他部分。
  - 🎨 [Tailwind CSS](https://tailwindcss.com) 与 [shadcn/ui](https://ui.shadcn.com) 提供前端组件。
  - 🤖 自动生成的前端客户端。
  - 🧪 [Playwright](https://playwright.dev) 用于端到端测试。
  - 🦇 支持深色模式。
- ☁️ [FastAPI Cloud](https://fastapicloud.com) 用于部署。
- 🐋 [Docker Compose](https://www.docker.com) 用于本地服务与自托管部署。
  - 📞 [Traefik](https://traefik.io) 作为带自动 HTTPS 的反向代理。
- 🔒 默认使用安全的密码哈希。
- 🔑 JWT（JSON Web Token）身份认证。
- 📫 基于邮件的密码找回。
- ✉️ [React Email](https://react.email) 用于邮件模板。
- 📬 [Mailpit](https://mailpit.axllent.org) 用于开发期间的本地邮件测试。
- ✅ 使用 [Pytest](https://pytest.org) 进行测试。
- 🏭 基于 GitHub Actions 的 CI（持续集成）与 CD（持续部署）。

### 控制台登录

![控制台登录截图](img/login.png)

### 控制台 - 管理端

![管理端控制台截图](img/dashboard.png)

### 控制台 - Items

![Items 控制台截图](img/dashboard-items.png)

### 控制台 - 深色模式

![深色模式截图](img/dashboard-dark.png)

### React Email 模板

![React Email 模板截图](img/react-email.png)

### Mailpit - 本地邮件测试

![Mailpit 截图](img/mailpit.png)

### 交互式 API 文档

![API 文档截图](img/docs.png)

## 如何使用

点击本页顶部的 **Use this template** 按钮即可创建一个新仓库。

## 后端开发

后端文档：[backend/README.md](./backend/README.md)。

## 前端开发

前端文档：[frontend/README.md](./frontend/README.md)。

## 部署

FastAPI Cloud 部署：[deployment.md](./deployment.md)。

使用 Docker Compose 自托管部署：[deployment-docker-compose.md](./deployment-docker-compose.md)。

## 开发

通用开发文档：[development.md](./development.md)。

其中包含本地 FastAPI 与 Vite 工作流、Docker Compose 服务、`.env` 配置等内容。

## 发布说明

请查看 [release-notes.md](./release-notes.md) 文件。

## 许可证

Full Stack FastAPI Template 采用 MIT 许可证。
