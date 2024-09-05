# app/database.py

from contextlib import contextmanager
from psycopg2 import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import pool, text, inspect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from typing import Generator

from backend.app.config import settings

Base = declarative_base()


class Database:
    """
    This class represents a database connection and session management object.
    It contains two attributes:

    - engine: A callable that represents the database engine.
    - session_maker: A callable that represents the session maker.
    """

    def __init__(self, uri):
        self.uri = uri
        self.engine = create_engine(
            uri,
            poolclass=pool.QueuePool,  # Use connection pooling
            pool_size=20,  # Adjust pool size based on your workload
            max_overflow=10,  # Adjust maximum overflow connections
            pool_recycle=3600,  # Periodically recycle connections (optional)
        )
        self.session_maker = sessionmaker(bind=self.engine, expire_on_commit=False)

    def get_session(self):
        with self.session_maker() as session:
            try:
                yield session
            except Exception as e:
                # Handle exception (logging, re-raise, etc.)
                print(f"Error while handling the session: {e}")
                raise

    def create_database(self):
        # Create the database if it does not exist
        try:
            if not database_exists(self.uri):
                # Create the database engine and session maker
                create_database(self.uri)
                print(f"Database {settings.POSTGRES_DBNAME} created!")
            else:
                print(f"Database {settings.POSTGRES_DBNAME} already exists!")

        except OperationalError as e:
            print(f"Error creating to database: {e}")

    def test_connection(self):
        try:
            with self.engine.connect() as conn:
                query = text("SELECT 1")

                # Test the connection
                conn.execute(query)

                print("Connection to the database established!")

        except OperationalError as e:
            print(f"Error connecting to the database: {e}")

    def create_tables(self):
        """
        Connects to a PostgreSQL database using environment variables for connection details.

        Returns:
            Database: A NamedTuple with engine and conn attributes for the database connection.
            None: If there was an error connecting to the database.

        """
        try:
            # Create all tables defined using the Base class (if not already created)
            with self.engine.begin():
                Base.metadata.create_all(self.engine)

            tables = self.get_table_names()

            print(f"Tables {tables} created!")

        except Exception as e:
            print(f"Error creating tables in the database: {str(e)}")

    def get_table_names(self):
        inspector = inspect(self.engine)
        return inspector.get_table_names()

    def print_tables(self):
        """
        Print the available tables in the database.
        """
        try:
            tables = self.get_table_names()
            print(f"Available tables: {tables}")
        except Exception as e:
            print(f"Error fetching table names: {str(e)}")

    def init(self):
        """
        Initializes the database connection and creates the tables.

        Args:
            uri (str): The database URI.

        Returns:
            Database: A NamedTuple with engine and conn attributes for the database connection.
            None: If there was an error connecting to the database.
        """

        try:
            self.create_database()
        except Exception as e:
            print(f"Error creating database: {e}")

        try:
            self.test_connection()
        except Exception as e:
            print(f"Error testing connection: {e}")

        try:
            self.create_tables()
        except Exception as e:
            print(f"Error creating tables: {e}")

        try:
            self.print_tables()
        except Exception as e:
            print(f"Error print available tables: {e}")

    def disconnect(self):
        """
        Clean up and close the database connection and session maker.
        """
        try:
            # Close all connections in the pool
            self.engine.dispose()
            print("Database connections closed.")
        except Exception as e:
            print(f"Error closing database connections: {str(e)}")

    def __repr__(self):
        return f"<Database(uri={self.uri})>"


# Load environment variables from the .env file
database = None


def init_database() -> Database:
    global database

    database = Database(settings.SQLALCHEMY_DATABASE_URI)
    database.init()

    return database


def disconnect_database() -> Database:
    global database

    database.disconnect()


async def get_db():
    """
    Define a dependency to create a database connection

    Returns:
        Database: A NamedTuple with engine and conn attributes for the database connection.
        None: If there was an error connecting to the database.
    """

    database = Database(settings.SQLALCHEMY_DATABASE_URI)
    database.init()

    yield database


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Define a dependency to create a database session asynchronously.

    Returns:
        AsyncSession: An async session for interacting with the database.
    """
    if database is None:
        init_database()

    with database.session_maker() as session:
        try:
            yield session
        finally:
            session.close()
