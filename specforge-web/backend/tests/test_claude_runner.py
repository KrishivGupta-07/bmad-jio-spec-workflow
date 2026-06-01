import pytest

from app.services.claude_runner import _extract_text, should_persist_message
from app.services.run_manager import is_auth_error_text


class TestIsAuthErrorText:
    def test_authentication_failed_marker(self):
        assert is_auth_error_text(
            '{"type":"system","subtype":"api_retry","error_status":401,'
            '"error":"authentication_failed"}'
        ) is True

    def test_invalid_credentials_message(self):
        assert is_auth_error_text("Failed to authenticate. API Error: 401 Invalid authentication credentials") is True

    def test_normal_message_is_not_auth_error(self):
        assert is_auth_error_text("Planning the PRD based on the brief.") is False

    def test_empty_is_not_auth_error(self):
        assert is_auth_error_text("") is False


class TestExtractText:
    def test_string_content(self):
        assert _extract_text({"content": "hello"}) == "hello"

    def test_message_text_blocks(self):
        payload = {
            "message": {
                "content": [
                    {"type": "text", "text": "line one"},
                    {"type": "text", "text": "line two"},
                ]
            }
        }
        assert _extract_text(payload) == "line one\nline two"

    def test_tool_only_blocks_return_empty(self):
        payload = {
            "message": {
                "content": [{"type": "tool_use", "id": "t1", "name": "Read"}]
            }
        }
        assert _extract_text(payload) == ""

    def test_empty_string_content(self):
        assert _extract_text({"content": ""}) == ""


class TestShouldPersistMessage:
    def test_rejects_blank(self):
        assert should_persist_message("assistant", "   ") is False

    def test_rejects_user_trigger_echo(self):
        assert should_persist_message("user", "Create PRD") is False

    def test_rejects_system_init(self):
        assert should_persist_message(
            "system",
            '{"type":"system","subtype":"init"}',
            {"type": "system", "subtype": "init"},
        ) is False

    def test_accepts_assistant(self):
        assert should_persist_message("assistant", "Planning the PRD.") is True

    def test_accepts_tool_use(self):
        assert should_persist_message("tool_use", "Read file.txt") is True

    def test_accepts_tool_result(self):
        assert should_persist_message("tool_result", "file contents here") is True

    def test_accepts_system_with_text(self):
        assert should_persist_message(
            "system",
            "Connected to workspace.",
            {"type": "system", "subtype": "info"},
        ) is True
