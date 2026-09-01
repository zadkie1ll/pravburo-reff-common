# pravburo-reff-common

Общий Git-сабмодуль сервисов Pravburo Referral.

Содержит:

- SQLAlchemy-модели схемы `referral`;
- единственную цепочку Alembic-миграций;
- общие Pydantic-контракты межсервисных команд;
- фабрику подключения к выделенной PostgreSQL `pravburo_ref`.

Этот репозиторий не содержит HTTP-приложения. В `site`, `crm` и `bounty` он
подключается как Git submodule в каталоге `common`.

```bash
cp .env.example .env
uv sync
uv run alembic history
uv run alembic upgrade head
```
