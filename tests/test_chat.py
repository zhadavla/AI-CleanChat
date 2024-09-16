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
        history_data = json.loads(history_message)
        assert history_data["type"] == "history", f"Expected type 'history', got: {history_data['type']}"

        # Receive new_user broadcast for "artem" joining the chat
        join_message = websocket.receive_text()
        join_data = json.loads(join_message)
        assert join_data["type"] == "new_user", f"Expected type 'new_user', got: {join_data['type']}"
        assert join_data["data"]["user"] == "artem", f"Expected 'artem' as user, got: {join_data['data']['user']}"
        assert join_data["data"][
                   "content"] == "has joined the chat!", f"Expected 'has joined the chat!', got: {join_data['data']['content']}"

        # Receive the list of online users (should contain only "artem")
        online_users_message = websocket.receive_text()
        online_users_data = json.loads(online_users_message)
        assert online_users_data[
                   "type"] == "online_users", f"Expected type 'online_users', got: {online_users_data['type']}"
        assert "artem" in online_users_data[
            "data"], f"Expected 'artem' in online users, got: {online_users_data['data']}"


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
        history_data = json.loads(history_message)
        assert history_data["type"] == "history"
        assert history_data["data"] == []  # Chat history should be empty initially

        # Recieve new_user broadcast for "artem" joining the chat
        new_user_message = wait_for_message(websocket)
        new_user_data = json.loads(new_user_message)
        assert new_user_data["type"] == "new_user"
        assert new_user_data["data"]["user"] == "artem"

        # Wait and validate the online users (should contain only "artem")
        online_users_message = wait_for_message(websocket)
        print(f"Received online users: {online_users_message}")
        online_users_data = json.loads(online_users_message)
        assert online_users_data["type"] == "online_users"
        assert online_users_data["data"] == ["artem"]

        # Simulate sending a message from "artem"
        websocket.send_text("my first message")

        # Wait and validate the broadcast of "artem: my first message"
        message_broadcast = wait_for_message(websocket)
        print(f"Received message broadcast: {message_broadcast}")
        message_data = json.loads(message_broadcast)
        assert message_data["data"]["user"] == "artem"
        assert message_data["data"]["content"] == "my first message"
