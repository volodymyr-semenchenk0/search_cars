from app.db import execute_query


class SourceRepository:
    @staticmethod
    def get_all() -> list[dict]:
        sql = "SELECT id, name, url FROM sources"
        return execute_query(sql)

    @staticmethod
    def get_by_id(source_id: int) -> dict | None:
        sql = "SELECT id, name, url FROM sources WHERE id = %s"
        rows = execute_query(sql, (source_id,))
        return rows[0] if rows else None

    @staticmethod
    def get_by_name(name: str) -> dict | None:
        sql = "SELECT id, name, url FROM sources WHERE name = %s"
        rows = execute_query(sql, (name,))
        return rows[0] if rows else None
