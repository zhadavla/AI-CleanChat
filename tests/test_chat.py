import json
import logging
import os
import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.websockets import WebSocketDisconnect

from ai_clean_chat_backend.HTTPServer import app, get_db
from ai_clean_chat_backend.database import Base

# Use SQLite file-based database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the database dependency to use the testing database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def setup_database():
    logging.basicConfig(level=logging.DEBUG)

    # Ensure any pre-existing test database file is removed before creating a new one
    if os.path.exists("./test.db"):
        logging.debug("Removing existing test database")
        os.remove("./test.db")

    # Create tables in the file-based SQLite database before each test
    logging.debug("Creating tables in test database")
    Base.metadata.create_all(bind=engine)

    yield

    # Drop tables after the test
    logging.debug("Dropping tables in test database")
    Base.metadata.drop_all(bind=engine)

    # Remove the test database file after the test
    if os.path.exists("./test.db"):
        logging.debug("Removing test database file")
        os.remove("./test.db")


# TestClient fixture for WebSocket testing
@pytest.fixture
def client():
    return TestClient(app)


# Basic WebSocket connection test
def test_websocket_basic_connection(client: TestClient, setup_database):
    # Establish a WebSocket connection
    with client.websocket_connect("/ws") as websocket:
        # Send the username "artem"
        websocket.send_text("artem")

        # Receive the initial chat history (should be empty at the start)
        history_message = websocket.receive_text()
        assert history_message.startswith("HISTORY:"), f"Expected history, got: {history_message}"

        # Receive the list of online users (should contain only "artem")
        online_users_message = websocket.receive_text()
        assert online_users_message.startswith("ONLINE_USERS:"), f"Expected online users, got: {online_users_message}"


def wait_for_message(websocket, timeout=3):
    start = time.time()
    while time.time() - start < timeout:
        try:
            message = websocket.receive_text()
            return message
        except WebSocketDisconnect:
            pass
        time.sleep(0.05)  # Poll every 50ms
    raise TimeoutError("Timeout waiting for WebSocket message")


def test_websocket_chat_flow(client: TestClient, setup_database):
    # Establish a WebSocket connection
    with client.websocket_connect("/ws") as websocket:
        # Simulate "artem" joining the chat
        websocket.send_text("artem")

        # Dynamically wait and validate the history (should be empty at the beginning)
        history_message = wait_for_message(websocket)
        print(f"Received history: {history_message}")
        assert history_message.startswith("HISTORY:")
        history = json.loads(history_message.split("HISTORY:")[1])
        assert history == []  # Chat history should be empty initially

        # Wait and validate the online users (should contain only "artem")
        online_users_message = wait_for_message(websocket)
        print(f"Received online users: {online_users_message}")
        assert online_users_message.startswith("ONLINE_USERS:")
        online_users = json.loads(online_users_message.split("ONLINE_USERS:")[1])
        assert online_users == ["artem"]

        # Wait for the "artem has joined the chat" broadcast
        join_message = wait_for_message(websocket)
        print(f"Received join message: {join_message}")
        assert join_message == "artem has joined the chat!"

        # Wait for the broadcasted online users again (should still contain "artem")
        online_users_message = wait_for_message(websocket)
        print(f"Received online users (again): {online_users_message}")
        assert online_users_message.startswith("ONLINE_USERS:")
        online_users = json.loads(online_users_message.split("ONLINE_USERS:")[1])
        assert online_users == ["artem"]

        # Simulate sending a message from "artem"
        websocket.send_text("my first message")

        # Wait and validate the broadcast of "artem: my first message"
        message_broadcast = wait_for_message(websocket)
        print(f"Received message broadcast: {message_broadcast}")
        assert message_broadcast == "artem: my first message"


if __name__ == "__main__":
    pytest.main()
