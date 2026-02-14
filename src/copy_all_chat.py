#!/usr/bin/env python3
"""
Module to copy the entire chat history to the clipboard.
"""

from helper import env_var, markdown_chat, read_chat


def run():
    """Read the chat history and format it for the clipboard."""
    chat_file = f"{env_var('alfred_workflow_data')}/chat.json"
    return markdown_chat(read_chat(chat_file), False)


if __name__ == "__main__":
    print(run())
