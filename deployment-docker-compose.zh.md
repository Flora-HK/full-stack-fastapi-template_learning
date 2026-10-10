# FastAPI 项目 - Docker Compose 部署

> **本文件说明**：本文是 `deployment-docker-compose.md` 的中文翻译版，对应上游文件 `deployment-docker-compose.md`，翻译日期 **2026-10-05**。
> 上游仓库持续更新，若日后英文原文有改动，本文可能滞后失效，请以英文原文为准。
> 本文件为新增文件，不修改上游任何内容。

你可以用 Docker Compose 把项目部署到你自己的远程服务器上。该部署配置包含 Traefik，用于处理 HTTPS 并把进来的流量路由到应用。

## 准备工作

* 准备一台可用的远程服务器。
* 为应用域名以及你想要暴露的支撑服务子域名配置指向该服务器的 DNS 记录，例如 `fastapi-project.example.com` 与 `adminer.fastapi-project.example.com`。
* 在远程服务器上安装并配置 [Docker](https://docs.docker.com/engine/install/)（Docker Engine，不是 Docker Desktop）。

## 复制代码

```bash
rsync -av --exclude=".git/" --filter=":- .gitignore" ./ root@your-server.example.com:/root/code/app/
```

`--filter=":- .gitignore"` 选项告诉 `rsync` 使用与 Git 相同的忽略规则，从而排除诸如 Python 虚拟环境之类的文件。

## 配置应用

### 环境变量

设置应用域名、项目名称与第一个超级用户的邮箱：

```bash
export DOMAIN=fastapi-project.example.com
export PROJECT_NAME="Full Stack FastAPI Project"
export FIRST_SUPERUSER=admin@example.com
```

你也可以按需配置以下环境变量：

* `SMTP_HOST`：你的邮件服务商提供的 SMTP 服务器主机。
* `SMTP_USER`：SMTP 服务器用户名。
* `EMAILS_FROM_EMAIL`：用于发送邮件的邮箱账号。
* `SENTRY_DSN`：Sentry 的 DSN。

### 密钥（Secrets）

为数据库密码、令牌签名密钥与第一个超级用户密码生成并设置安全的值：

```bash
export POSTGRES_PASSWORD="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export FIRST_SUPERUSER_PASSWORD="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
```

若要使用需要认证的邮件服务商，还需设置 `SMTP_PASSWORD`。

## 部署

```bash
cd /root/code/app/
docker compose -f compose.yml -f compose.deploy.yml build
docker compose -f compose.yml -f compose.deploy.yml run --rm backend bash scripts/prestart.sh
docker compose -f compose.yml -f compose.deploy.yml up -d
```

`compose.deploy.yml` 文件为共享的 `compose.yml` 配置追加了 HTTPS 与自动证书处理。显式列出这两个文件可以排除 `compose.override.yml` 中的本地设置。

后端的 Docker 镜像会自行构建前端，因此服务器上不需要 Bun，也不需要预先构建好的前端文件。

## 使用 GitHub Actions 部署

仓库自带的 `.github/workflows/deploy-docker-compose.yml` 工作流会在你从 GitHub Actions 手动触发时，在服务器上执行部署命令。

只对你信任其贡献者与工作流代码的仓库使用自托管 runner。GitHub 建议在私有仓库中使用自托管 runner，因为工作流会直接在 runner 机器上执行。

### 配置仓库变量与密钥

在仓库中进入 **Settings** > **Secrets and variables** > **Actions**，添加以下仓库变量：

* `DOMAIN`
* `PROJECT_NAME`
* `FIRST_SUPERUSER`

要启用邮件功能，请添加以下可选仓库变量：

* `SMTP_HOST`
* `SMTP_USER`
* `EMAILS_FROM_EMAIL`

要启用 Sentry，请添加可选的 `SENTRY_DSN` 仓库变量。

添加以下仓库密钥：

* `POSTGRES_PASSWORD`
* `SECRET_KEY`
* `FIRST_SUPERUSER_PASSWORD`

要使用需要认证的邮件服务商，请添加可选的 `SMTP_PASSWORD` 仓库密钥。

### 安装自托管 runner

在服务器上创建一个专用用户，并授予它访问 Docker 的权限：

```bash
sudo adduser github
sudo usermod -aG docker github
sudo su - github
```

在 GitHub 仓库中进入 **Settings** > **Actions** > **Runners**，选择 **New self-hosted runner**，选择 Linux，并按 GitHub 给出的命令下载、配置并注册 runner。把它安装在 `/home/github/actions-runner`。

注册 runner 之后，退出 `github` 用户会话，并把 runner 安装为系统服务：

```bash
exit
cd /home/github/actions-runner
sudo ./svc.sh install github
sudo ./svc.sh start
sudo ./svc.sh status
```

参见 GitHub 的指南：[添加自托管 runner](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners) 与 [把 runner 配置为服务](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/configure-the-application?platform=linux)。

### 执行部署

当 runner 在线后，打开仓库的 **Actions** 标签页，选择 **Deploy with Docker Compose**，然后选择 **Run workflow**。

## URL

把 `fastapi-project.example.com` 替换为你的域名。

应用（前端与 API）：`https://fastapi-project.example.com`

交互式 API 文档：`https://fastapi-project.example.com/docs`

Adminer：`https://adminer.fastapi-project.example.com`
