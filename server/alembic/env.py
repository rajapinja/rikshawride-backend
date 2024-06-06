import os
import sys
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Append the path to your application to the sys.path
sys.path.append(os.getcwd())

print('sys.path :',sys.path)

print('os.environ:',os.environ.get('PYTHONPATH'))

# from rikshawride.models import Base  # Import your SQLAlchemy Base classass

# Import and configure your database settings
config = context.config
config.set_main_option('sqlalchemy.url', 'mysql+mysqlconnector://root:password@localhost/rikshawride')
target_metadata = Base.metadata  # Use the metadata from your SQLAlchemy Base

# Initialize the engine and connection
engine = engine_from_config(
    config.get_section(config.config_ini_section),
    prefix='sqlalchemy.',
    poolclass=pool.NullPool
)

# Register the engine and metadata with the context
context.configure(
    connection=engine.connect(),
    target_metadata=target_metadata
)

# Run the Alembic command
with context.begin_transaction():
    context.run_migrations()
