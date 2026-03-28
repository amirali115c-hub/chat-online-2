"""
Test fixtures for chatonline tests.
"""
import os
import sys
import pytest
import tempfile

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment before any imports
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///test_chat_online.db'
os.environ['ADMIN_USERNAME'] = 'testadmin'
os.environ['ADMIN_PASSWORD'] = 'testpassword123'
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only-32chars'
os.environ['JWT_SECRET'] = 'test-jwt-secret-key-for-testing-only'


@pytest.fixture
def app():
    """Create a test Flask app with an in-memory SQLite database."""
    # Patch database before importing app
    original_init = None

    import database as db_module
    db_module.DATABASE_URL = 'sqlite:///test_chat_online.db'
    db_module.USE_POSTGRES = False
    db_module.DB_FILE = 'test_chat_online.db'

    # Remove old db file if exists
    test_db = 'test_chat_online.db'
    if os.path.exists(test_db):
        os.remove(test_db)

    db_module.init_database()

    yield db_module

    # Cleanup
    if os.path.exists(test_db):
        os.remove(test_db)


@pytest.fixture
def client(app):
    """Create a test client."""
    from app import app as flask_app
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def app_context(app):
    """Provide an app context."""
    from app import app as flask_app
    with flask_app.app_context():
        yield
