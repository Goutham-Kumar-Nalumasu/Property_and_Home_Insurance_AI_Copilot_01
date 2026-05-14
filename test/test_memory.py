from app.memory import MemoryManager


def test_memory_update(tmp_path):
    memory_file = tmp_path / "sessions.json"
    manager = MemoryManager(memory_file=memory_file)

    session_id = "test-session"
    manager.update(session_id, {"policy_type": "Standard"})

    memory = manager.get(session_id)

    assert memory["policy_type"] == "Standard"