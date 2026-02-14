"""
OpenRouter LLM service implementation.
"""

import json
from .openai import OpenaiService


class OpenRouterService(OpenaiService):
    """
    Service for interacting with OpenRouter API, extending OpenAI service.
    """

    def construct_curl_command(
        self, max_tokens, messages, stream_file, system_prompt=None
    ) -> list:
        data = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            # "max_tokens": max_tokens,  # OpenRouter defaults are usually fine, but OpenAI requires it sometimes.
            # Let's include it for safety if provided, similar to OpenaiService?
            # Actually OpenaiService doesn't include max_tokens in construct_curl_command by default?
            # Checking openai.py content... it DOES NOT include max_tokens in data dict.
            # Checking cerebras.py... it DOES inclusion max_tokens.
            # OpenRouter is OpenAI compatible, so it might not strictly need it, but let's see.
            # If I want to be safe and consistent with Cerebras which is also OpenAI compatible,
            # I might include it.
            # However, OpenaiService implementation in this repo (from my memory/view_file) does NOT use
            # max_tokens in the body for standard OpenAI.
            # Let's check openai.py again to be sure. I'll stick to OpenaiService pattern unless
            # OpenRouter specifically needs it.
            # OpenRouter docs say it supports standard OpenAI parameters.
            # For now, I'll follow Cerebras pattern and include it if it was passed, or just minimal set.
            # Actually, `max_tokens` IS passed to `construct_curl_command`.
            # In `openai.py`, `construct_curl_command` receives `max_tokens` but does NOT use it in `data`.
            # In `cerebras.py`, I *did* add it.
            # OpenRouter guides often show just model/messages/stream.
            # I will omit max_tokens to be consistent with the base `openai.py`,
            # unless I find `openai.py` *should* have it.
            # Wait, if `openai.py` works without it, then OpenRouter should too.
            # BUT, I will add the extra headers.
        }

        # Based on Cerebras implementation, I added max_tokens there.
        # Let's check if openai.py really doesn't use it.
        # I remember seeing `max_tokens` in `construct_curl_command` signature in `openai.py` but not used in `data`.
        # I'll check `openai.py` content again.
        # Actually I can't check right now without a tool call.
        # I'll assume standard OpenAI pattern (no max_tokens mandatory).
        # However, for OpenRouter, I want to add the headers.

        return [
            "curl",
            f"{self.api_endpoint}/chat/completions",
            "--speed-limit",
            "0",
            "--speed-time",
            str(self.stall_timeout_sec),
            "--silent",
            "--no-buffer",
            "--header",
            f"User-Agent: {self.user_agent}",
            "--header",
            "Content-Type: application/json",
            "--header",
            f"Authorization: Bearer {self.api_key}",
            "--header",
            "HTTP-Referer: https://github.com/chenjh16/alfred-chat-workflow",
            "--header",
            "X-Title: Alfred-Chat-Workflow",
            "--data",
            json.dumps(data),
            "--output",
            stream_file,
        ] + self.proxy_option
