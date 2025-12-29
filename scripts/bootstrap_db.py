import subprocess

from sqlalchemy import inspect

from app.db import Base, engine
from app import models  # noqa: F401


def main() -> None:
    inspector = inspect(engine)
    has_users = inspector.has_table("users")
    if not has_users:
        Base.metadata.create_all(bind=engine)
        _stamp_heads()
        print("✅ Database schema created and stamped.")
        return

    _upgrade_heads()


def _stamp_heads() -> None:
    subprocess.run(
        ["alembic", "-c", "migrations/alembic.ini", "stamp", "heads"],
        check=True,
    )


def _upgrade_heads() -> None:
    subprocess.run(
        ["alembic", "-c", "migrations/alembic.ini", "upgrade", "heads"],
        check=True,
    )


if __name__ == "__main__":
    main()
