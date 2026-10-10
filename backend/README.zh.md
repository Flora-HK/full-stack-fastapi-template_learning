# FastAPI 项目 - 后端

> **本文件说明**：本文是 `backend/README.md` 的中文翻译版，对应上游文件 `backend/README.md`，翻译日期 **2026-10-05**。
> 上游仓库持续更新，若日后英文原文有改动，本文可能滞后失效，请以英文原文为准。
> 本文件为新增文件，不修改上游任何内容。

## 环境要求

* [Docker](https://www.docker.com/)。
* [uv](https://docs.astral.sh/uv/) 用于 Python 包与环境管理。

## 本地开发

在本地运行后端，并连接 Docker Compose 中的 PostgreSQL。

在项目根目录下，启动 PostgreSQL 与 Mailpit：

```console
$ docker compose up -d db mailpit
```

然后在 `./backend/` 目录下安装依赖、准备数据库并启动开发服务器：

```console
$ uv sync
$ uv run bash scripts/prestart.sh
$ uv run fastapi dev
```

API 可通过 `http://localhost:8000` 访问，自动生成的交互式文档位于 `http://localhost:8000/docs`。

## 通用工作流

后端命令请在 `./backend/` 目录下通过 `uv run` 执行。请确保你的编辑器使用项目根目录下的 `.venv/bin/python` 作为 Python 解释器。

在 `./backend/app/models.py` 中修改或新增 SQLModel 模型（对应数据与数据表），在 `./backend/app/api/` 中修改 API 端点，在 `./backend/app/crud.py` 中添加 CRUD（增删改查）工具函数。

## VS Code

项目中已配置好通过 VS Code 调试器运行后端的方式，因此你可以使用断点、暂停并查看变量等。

该配置同样已就绪，你可以通过 VS Code 的 Python 测试面板运行测试。

## 使用 Docker Compose 运行全栈

要运行包含后端与已构建前端的 Docker Compose 环境：

```console
$ docker compose run --rm backend bash scripts/prestart.sh
$ docker compose watch
```

应用可通过 `http://localhost:8000` 访问。

### Docker Compose Override

`compose.override.yml` 文件包含本地的端口发布设置、源码同步、自动镜像重建以及后端热重载。当你不显式指定文件列表直接运行 `docker compose` 时，Docker Compose 会自动应用它。

要在后端容器中打开一个 shell：

```console
$ docker compose exec backend bash
```

## 后端测试

在 `backend` 目录下运行后端测试：

```console
$ uv run bash scripts/test.sh
```

测试使用 Pytest 运行。请在 `./backend/tests/` 中修改现有测试或添加新测试。

如果你使用 GitHub Actions，测试会自动运行。

### 测试正在运行的整套服务

如果你的服务栈已经启动，只想运行测试，可以使用：

```bash
docker compose exec backend bash scripts/tests-start.sh
```

`/app/backend/scripts/tests-start.sh` 脚本会调用 `pytest`。如果你需要向 `pytest` 传递额外参数，可以把它们加在该命令后面，参数会被转发。

例如，要在遇到第一个错误时停止：

```bash
docker compose exec backend bash scripts/tests-start.sh -x
```

### 测试覆盖率

测试运行时会生成 `htmlcov/index.html`。在浏览器中打开它即可查看测试覆盖率。

## 数据库迁移（Migrations）

每次修改模型时，请务必创建一次修订（revision）并用该修订升级数据库。在 `backend` 目录下，使用 `uv` 针对 PostgreSQL 容器运行 Alembic：

* Alembic 已配置为从 `./backend/app/models.py` 导入你的 SQLModel 模型。

* 修改模型后（例如新增一列），创建修订：

```console
$ uv run alembic revision --autogenerate -m "Add column last_name to User model"
```

* 将 alembic 目录中生成的文件提交到 git 仓库。

* 创建修订之后，在数据库中执行迁移（这一步才会真正改变数据库）：

```console
$ uv run alembic upgrade head
```

如果你完全不想使用迁移，请取消注释 `./backend/app/core/db.py` 中以下内容的注释：

```python
SQLModel.metadata.create_all(engine)
```

并注释掉 `scripts/prestart.sh` 中的这一行：

```console
$ alembic upgrade head
```

如果你不想沿用默认模型，想在完全没有历史修订的情况下从一开始就删除或修改它们，可以删掉 `./backend/app/alembic/versions/` 下的修订文件（`.py` 文件），然后按上述方式创建第一个迁移。

## 邮件模板

邮件模板使用 [React Email](https://react.email) 编写，位于 `./packages/react-email/`。`emails` 目录下每个组件对应一封邮件，`ui` 目录下是共享组件（layout、heading、button、link、callout）。

`./backend/app/email-templates/` 中渲染出的 HTML 由这些组件生成。它才是应用实际发送的内容，**不应手动编辑**。

要在编辑时预览邮件，请在项目根目录启动开发服务器：

```console
$ bun run email:dev
```

来自后端的值在组件 props 中以 Jinja 占位符声明，例如 `username = "{{ username }}"`。每封邮件的上下文在 `./backend/app/utils.py` 的 `generate_*_email()` 中构建，因此新增占位符时也需要在那里添加。

完成后，重新生成应用使用的模板：

```console
$ bun run email:export
```
