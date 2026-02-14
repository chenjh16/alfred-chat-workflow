"""
Anthropic LLM service implementation.
"""

import json
from typing import Tuple, Optional, Any

from .base import LLMService


class AnthropicService(LLMService):
    """
    Service for interacting with Anthropic API.
    """

    def construct_curl_command(
        self, max_tokens, messages, stream_file, system_prompt=None
    ) -> list:
        data = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages,
            "stream": True,
        }

        if system_prompt:
            data["system"] = system_prompt

        return [
            "curl",
            f"{self.api_endpoint}/v1/messages",
            "--speed-limit",
            "0",
            "--speed-time",
            str(self.stall_timeout_sec),  # Abort stalled connection after a few seconds
            "--silent",
            "--no-buffer",
            "--header",
            "Content-Type: application/json",
            "--header",
            f"User-Agent: {self.user_agent}",
            "--header",
            f"x-api-key: {self.api_key}",
            "--header",
            "anthropic-version: 2023-06-01",
            "--data",
            json.dumps(data),
            "--output",
            stream_file,
        ] + self.proxy_option

    def parse_stream_response(self, stream_string) -> Tuple[str, Optional[str], bool]:
        # 统一错误呈现：若为一次性 JSON 错误体，则直接回显可读错误信息
        if stream_string.startswith("{"):
            try:
                obj = json.loads(stream_string)
            except Exception:
                return "Response body is not valid json.", "", True
            err = obj.get("error") or {}
            if err:
                etype = err.get("type", "Error")
                emsg = err.get("message", "Unknown Error")
                return f"{etype}: {emsg}", "", True
            return json.dumps(obj, ensure_ascii=False), "", True

        lines = stream_string.strip().split("\n")

        chunks = []
        current_event: dict[str, Any] = {}

        for line in lines:
            if line.startswith("event:"):
                current_event = {}
                current_event["event"] = line[len("event: ") :].strip()
            elif line.startswith("data:"):
                data = line[len("data: ") :].strip()
                try:
                    current_event["data"] = json.loads(data)
                except json.JSONDecodeError:
                    current_event["data"] = None
                chunks.append(current_event)

        response_text = ""
        has_stopped = False
        for current_event in chunks:
            if current_event["event"] == "content_block_start":
                response_text = response_text + current_event["data"].get(
                    "content_block", {}
                ).get("text", "")
            elif current_event["event"] == "content_block_delta":
                response_text = response_text + current_event["data"].get(
                    "delta", {}
                ).get("text", "")
            elif current_event["event"] == "message_stop":
                has_stopped = True
                break
            elif current_event["event"] == "error":
                # 直接回显错误详情并终止
                err_obj = (
                    current_event["data"].get("error", {})
                    if current_event.get("data")
                    else {}
                )
                etype = err_obj.get("type", "Error")
                emsg = err_obj.get("message", "Unknown Error")
                return f"{etype}: {emsg}", "", True

        # 非错误结束场景下仅返回内容；错误已在上面直接回显
        return response_text, None, has_stopped

    def _prepare_messages(self, system_prompt, context_chat):
        """Anthropic passes system_prompt via API body, not as a message."""
        return context_chat
