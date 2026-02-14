"""
Cerebras LLM service implementation.
"""

import json

from .openai import OpenaiService


class CerebrasService(OpenaiService):
    """
    Service for interacting with Cerebras LLM API, compatible with OpenAI.
    """

    def construct_curl_command(
        self, max_tokens, messages, stream_file, system_prompt=None
    ) -> list:
        data = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "max_tokens": max_tokens,
        }

        return [
            "curl",
            f"{self.api_endpoint}/v1/chat/completions",
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
            "--data",
            json.dumps(data),
            "--output",
            stream_file,
        ] + self.proxy_option
