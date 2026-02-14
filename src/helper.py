"""
Helper functions for file operations and environment variable handling.
"""

import os
import json
import shutil
from pathlib import Path


def env_var(var_name):
    """Retrieve an environment variable."""
    return os.environ.get(var_name)


def user_signature():
    """Return the markdown signature for the user."""
    return "**You:**\n\n"


def assistant_signature():
    """Return the markdown signature for the assistant."""
    return "**Assistant:**\n\n"


def make_dir(path):
    """Create a directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


def dir_contents(path):
    """Return a sorted list of file paths in a directory."""
    return sorted(
        [
            str(p)
            for p in Path(path).iterdir()
            if p.is_file() and not p.name.startswith(".")
        ]
    )


def mv(init_path, target_path):
    """Move a file from source to destination."""
    shutil.move(init_path, target_path)


def file_exists(path):
    """Check if a file exists."""
    return os.path.exists(path)


def file_modified(path):
    """Return the last modification time of a file."""
    return os.path.getmtime(path)


def delete_file(path):
    """Delete a file if it exists."""
    if file_exists(path):
        os.remove(path)


def write_file(path, text):
    """Write text to a file."""
    with open(path, "w", encoding="utf-8") as file:
        file.write(text)


def read_chat(path):
    """Read chat history from a file."""
    if not file_exists(path):
        return []
    with open(path, "r", encoding="utf-8") as file:
        chat_string = file.read()
    return json.loads(chat_string)


def trash_chat(path):
    """Move a chat file to the trash."""
    shutil.move(path, os.path.expanduser("~/.Trash"))


def append_chat(path, message):
    """Append a message to the chat history file."""
    ongoing_chat = read_chat(path) + [message]
    chat_string = json.dumps(ongoing_chat)
    write_file(path, chat_string)


def markdown_chat(messages, ignore_last_interrupted=True):
    """Format chat messages as markdown."""
    result = ""
    for index, current in enumerate(messages):
        role = current.get("role")
        content = current.get("content") or ""
        if role == "assistant":
            result += assistant_signature() + content + "\n\n"
        elif role == "user":
            lines = content.split("\n") if content else []
            user_message = user_signature() + "\n".join(lines)
            user_twice = (
                index + 1 < len(messages) and messages[index + 1].get("role") == "user"
            )
            last_message = index == len(messages) - 1
            if user_twice or (last_message and not ignore_last_interrupted):
                result += f"{user_message}\n\n[Answer Interrupted]\n\n"
            else:
                result += f"{user_message}\n\n"
        result += "---\n"
    return result


def no_archives():
    """Return a JSON response indicating no archives were found."""
    return json.dumps(
        {
            "items": [
                {
                    "title": "No Chat Histories Found",
                    "subtitle": "Archives are created when starting new conversations",
                    "valid": False,
                }
            ]
        }
    )
