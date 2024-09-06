import sys
import subprocess
from datetime import datetime


async def generate_migrations():
    """Generate a new Alembic migration script with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    message = f"auto_generated_migration_{timestamp}"
    command = [
        sys.executable,
        "-m",
        "alembic",
        "revision",
        "--autogenerate",
        "-m",
        message,
    ]
    subprocess.run(command, check=True)


async def run_migrations():
    """Run Alembic migrations."""
    command = [sys.executable, "-m", "alembic", "upgrade", "head"]
    process = subprocess.run(command, check=True)
    if process.returncode != 0:
        raise RuntimeError("Alembic migrations failed")
