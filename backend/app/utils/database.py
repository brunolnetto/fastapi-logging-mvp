from sqlalchemy import text
from sqlalchemy.orm import Session


def get_table_size(
    session: Session, table_name: str, schema_name: str = "public"
) -> dict:
    """
    Get the size of a PostgreSQL table including its indexes and the total size.

    Args:
        session (Session): SQLAlchemy session object.
        table_name (str): The name of the table to measure.
        schema_name (str): The schema where the table resides. Defaults to 'public'.

    Returns:
        dict: A dictionary with keys 'table_size', 'indexes_size', and 'total_size' containing human-readable size strings.
    """
    query = text(
        """
        SELECT 
            pg_size_pretty(pg_table_size(c.oid)) AS table_size,
            pg_size_pretty(pg_indexes_size(c.oid)) AS indexes_size,
            pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size
        FROM 
            pg_class c
        LEFT JOIN 
            pg_namespace n ON n.oid = c.relnamespace
        WHERE 
            n.nspname = :schema_name 
            AND c.relname = :table_name
    """
    )

    result = session.execute(
        query, {"schema_name": schema_name, "table_name": table_name}
    ).fetchone()

    if result:
        return {
            "table_size": result.table_size,
            "indexes_size": result.indexes_size,
            "total_size": result.total_size,
        }
    else:
        raise ValueError(f"Table {table_name} not found in schema {schema_name}")
