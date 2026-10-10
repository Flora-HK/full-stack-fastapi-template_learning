# FastAPI 项目 - 部署

> **本文件说明**：本文是 `deployment.md` 的中文翻译版，对应上游文件 `deployment.md`，翻译日期 **2026-10-05**。
> 上游仓库持续更新，若日后英文原文有改动，本文可能滞后失效，请以英文原文为准。
> 本文件为新增文件，不修改上游任何内容。

使用仓库自带的 GitHub Actions 工作流把项目部署到 [FastAPI Cloud](https://fastapicloud.com)。

## 创建 FastAPI Cloud 应用

在 FastAPI Cloud 中创建一个应用，并把它的 [Application Directory](https://fastapicloud.com/docs/builds-and-deployments/application-directory/) 设置为 `backend`。

通过 [Neon](https://fastapicloud.com/docs/integrations/neon-integration/) 或 [Supabase](https://fastapicloud.com/docs/integrations/supabase-integration/) 集成连接一个 PostgreSQL 数据库。这两种集成都会自动配置 `DATABASE_URL` 密钥。你也可以为其他 PostgreSQL 服务商手动配置 `DATABASE_URL`。

## 配置应用

### 环境变量

在 FastAPI Cloud 应用中添加以下必需的[环境变量](https://fastapicloud.com/docs/builds-and-deployments/environment-variables/)：

* `PROJECT_NAME`：项目名称，用于 API 文档与邮件中。
* `FIRST_SUPERUSER`：第一个超级用户的邮箱地址。
* `FRONTEND_HOST`：应用的公开 URL，例如自动生成的 `https://your-app.fastapicloud.dev` 或自定义域名。

要启用邮件功能，请添加以下可选环境变量并填入你的邮件服务商提供的值：

* `SMTP_HOST`
* `SMTP_USER`
* `EMAILS_FROM_EMAIL`

要启用 Sentry，请配置 `SENTRY_DSN`。

### 密钥（Secrets）

添加以下必需的值，并把它们标记为密钥：

* `SECRET_KEY`：用于签名安全令牌的密钥。
* `FIRST_SUPERUSER_PASSWORD`：第一个超级用户的密码。
* `DATABASE_URL`：PostgreSQL 连接 URL，使用数据库集成时会自动配置。

要使用需要认证的邮件服务商启用邮件功能，请把 `SMTP_PASSWORD` 也添加为密钥。

你可以用以下命令为 `SECRET_KEY` 与 `FIRST_SUPERUSER_PASSWORD` 生成安全的值：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 配置持续部署

仓库自带的 `.github/workflows/deploy.yml` 工作流会在有改动推送到 `master` 时构建前端、准备数据库并部署应用。你也可以在 **Actions** 标签页中手动运行它。

登录 FastAPI Cloud，并把[部署令牌](https://fastapicloud.com/docs/advanced-features/deploy-tokens/)与应用 ID 配置为 GitHub 仓库密钥：

```bash
uv run fastapi login
uv run fastapi cloud setup-ci --secrets-only --app-id <your-app-id>
```

如果已安装并认证了 GitHub CLI，该命令会自动配置 `FASTAPI_CLOUD_TOKEN` 与 `FASTAPI_CLOUD_APP_ID`。否则，它会把这些值打印出来，你可以在仓库的 **Settings** > **Secrets and variables** > **Actions** 中手动添加。

该工作流会在部署前执行数据库迁移并创建第一个超级用户。在仓库的 **Settings** > **Secrets and variables** > **Actions** 页面中，添加以下仓库变量：

* `PROJECT_NAME`
* `FIRST_SUPERUSER`

添加以下仓库密钥：

* `DATABASE_URL`
* `SECRET_KEY`
* `FIRST_SUPERUSER_PASSWORD`

请使用与 FastAPI Cloud 中相同的值。对于 `DATABASE_URL`，请使用你的数据库服务商提供的连接 URL。数据库必须能被 GitHub 托管的 runner 访问，这样准备步骤才能连上它。

部署工作流会执行以下步骤：

1. 安装并构建前端，产物输出到 `backend/app/frontend`。
2. 运行 `backend/scripts/prestart.sh` 以应用数据库迁移并创建第一个超级用户。
3. 使用 `uv run fastapi deploy` 部署项目。

## URL

把 `your-app.fastapicloud.dev` 替换为你的 FastAPI Cloud 应用 URL。

应用（前端与 API）：`https://your-app.fastapicloud.dev`

交互式 API 文档：`https://your-app.fastapicloud.dev/docs`

## Docker Compose

若要部署到你自己的服务器，请参阅 [Docker Compose 部署指南](./deployment-docker-compose.md)。

## GitHub 仓库自动化

安装以下 GitHub App 以启用仓库自带的自动化功能：

* [Latest Changes](https://github.com/apps/latest-changes) 会在拉取请求合并时更新 `release-notes.md`。
* [PR Push](https://github.com/apps/pr-push) 让 pre-commit 工作流能把自动修复推送到拉取请求分支。
* [PR Submit](https://github.com/apps/pr-submit) 让 **Bump pre-commit hooks** 与 **Prepare Release** 工作流能够创建拉取请求。

要用 [Smokeshow](https://github.com/samuelcolvin/smokeshow) 发布代码覆盖率，请添加 `SMOKESHOW_AUTH_KEY` 作为仓库密钥。
