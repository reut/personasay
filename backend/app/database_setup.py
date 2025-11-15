#!/usr/bin/env python3
"""
Database Setup and Migration Script for PersonaSay LangChain
Creates database tables and handles migrations for production deployment
"""

import sys

from langchain_personas import Base
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.logging_config import get_logger

logger = get_logger(__name__)


class DatabaseSettings(BaseSettings):
    """Database configuration"""

    database_url: str = "sqlite:///./personasay.db"

    class Config:
        env_file = ".env"


def create_database_engine(database_url: str) -> Engine:
    """Create database engine with appropriate settings"""
    if database_url.startswith("sqlite"):
        # SQLite settings for development
        engine = create_engine(database_url, connect_args={"check_same_thread": False}, echo=False)
    elif database_url.startswith("postgresql"):
        # PostgreSQL settings optimized for production
        engine = create_engine(
            database_url,
            pool_size=20,  # Number of connections in pool
            max_overflow=40,  # Max extra connections when busy
            pool_recycle=3600,  # Recycle connections after 1 hour
            pool_pre_ping=True,  # Test connections before use
            echo=False,  # Disable SQL echo in production
            pool_timeout=30,  # Connection timeout
        )
    else:
        # Generic settings
        engine = create_engine(database_url, echo=False)

    return engine


def create_tables(engine: Engine):
    """Create all database tables"""
    logger.info("Creating database tables...")

    try:
        # Create all tables defined in the models
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Verify tables were created
        with engine.connect() as conn:
            # Check if tables exist
            if engine.dialect.name == "sqlite":
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            elif engine.dialect.name == "postgresql":
                result = conn.execute(
                    text("SELECT tablename FROM pg_tables WHERE schemaname='public';")
                )
            else:
                logger.warning("Cannot verify tables for this database type")
                return

            tables = [row[0] for row in result]
            logger.info(f"Created tables: {', '.join(tables)}")

    except Exception as e:
        logger.error(f"Error creating tables: {e}", exc_info=True)
        sys.exit(1)


def setup_database_indexes(engine: Engine):
    """Create indexes for better performance"""
    logger.info("Creating database indexes...")

    try:
        with engine.connect() as conn:
            # Index for persona_id lookups
            conn.execute(
                text(
                    """
                CREATE INDEX IF NOT EXISTS idx_persona_memories_persona_id
                ON persona_memories(persona_id);
            """
                )
            )

            # Index for session_id lookups
            conn.execute(
                text(
                    """
                CREATE INDEX IF NOT EXISTS idx_persona_memories_session_id
                ON persona_memories(session_id);
            """
                )
            )

            # Index for timestamp ordering
            conn.execute(
                text(
                    """
                CREATE INDEX IF NOT EXISTS idx_persona_memories_timestamp
                ON persona_memories(timestamp);
            """
                )
            )

            # Composite index for efficient queries
            conn.execute(
                text(
                    """
                CREATE INDEX IF NOT EXISTS idx_persona_memories_persona_session
                ON persona_memories(persona_id, session_id);
            """
                )
            )

            conn.commit()
            logger.info("Database indexes created successfully")

    except Exception as e:
        logger.error(f"Error creating indexes: {e}", exc_info=True)


def seed_database(engine: Engine):
    """Seed database with initial data if needed"""
    logger.info("Seeding database with initial data...")

    try:
        with engine.connect() as conn:
            # Check if we need to seed data
            result = conn.execute(text("SELECT COUNT(*) FROM persona_memories;"))
            count = result.scalar()

            if count == 0:
                logger.info("Database is empty, seeding with welcome messages...")

                # Insert welcome messages for common personas
                welcome_messages = [
                    {
                        "persona_id": "system",
                        "session_id": "system_init",
                        "message_type": "system",
                        "content": "PersonaSay LangChain system initialized successfully",
                    }
                ]

                for msg in welcome_messages:
                    conn.execute(
                        text(
                            """
                        INSERT INTO persona_memories (persona_id, session_id, message_type, content, meta_data)
                        VALUES (:persona_id, :session_id, :message_type, :content, :meta_data);
                    """
                        ),
                        {**msg, "meta_data": "{}"},
                    )

                conn.commit()
                logger.info("Database seeded successfully")
            else:
                logger.info(f"Database already contains {count} memory records")

    except Exception as e:
        logger.error(f"Error seeding database: {e}", exc_info=True)


def backup_database(engine: Engine, backup_path: str = None):
    """Create database backup (SQLite only)"""
    if not engine.url.drivername == "sqlite":
        logger.warning("Backup only supported for SQLite databases")
        return

    import shutil
    from datetime import datetime

    if not backup_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"personasay_backup_{timestamp}.db"

    try:
        db_path = str(engine.url).replace("sqlite:///", "")
        shutil.copy2(db_path, backup_path)
        logger.info(f"Database backup created: {backup_path}")
    except Exception as e:
        logger.error(f"Error creating backup: {e}", exc_info=True)


def check_database_health(engine: Engine):
    """Check database health and connectivity"""
    logger.info("Checking database health...")

    try:
        with engine.connect() as conn:
            # Test basic connectivity
            conn.execute(text("SELECT 1;"))

            # Check table structure
            if engine.dialect.name == "sqlite":
                result = conn.execute(
                    text(
                        """
                    SELECT name, sql FROM sqlite_master
                    WHERE type='table' AND name IN ('persona_memories', 'conversation_sessions');
                """
                    )
                )
            elif engine.dialect.name == "postgresql":
                result = conn.execute(
                    text(
                        """
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema='public' AND table_name IN ('persona_memories', 'conversation_sessions');
                """
                    )
                )

            tables = [row[0] for row in result]
            required_tables = ["persona_memories", "conversation_sessions"]
            missing_tables = set(required_tables) - set(tables)

            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False

            # Check data integrity
            memory_count = conn.execute(text("SELECT COUNT(*) FROM persona_memories;")).scalar()
            session_count = conn.execute(
                text("SELECT COUNT(*) FROM conversation_sessions;")
            ).scalar()

            logger.info("Database health check passed")
            logger.info(f"Memory records: {memory_count}")
            logger.info(f"Sessions: {session_count}")
            return True

    except Exception as e:
        logger.error(f"Database health check failed: {e}", exc_info=True)
        return False


def main():
    """Main setup function"""
    logger.info("PersonaSay LangChain Database Setup")
    logger.info("=" * 50)

    # Load settings
    settings = DatabaseSettings()
    logger.info(f"Database URL: {settings.database_url}")

    # Create engine
    engine = create_database_engine(settings.database_url)

    # Test connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Cannot connect to database: {e}", exc_info=True)
        sys.exit(1)

    # Setup database
    create_tables(engine)
    setup_database_indexes(engine)
    seed_database(engine)

    # Health check
    if check_database_health(engine):
        logger.info("Database setup completed successfully!")
        logger.info("Your PersonaSay LangChain system is ready for deployment.")
    else:
        logger.error("Database setup completed with issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
