#!/usr/bin/env python3
"""
Main entry point for the chat workflow using various LLM services.
"""

import json
import sys
from typing import Optional

from helper import append_chat, env_var, file_exists, markdown_chat, read_chat
from llm import (
    AnthropicService,
    CerebrasService,
    DeepseekService,
    GeminiService,
    OllamaService,
    OpenaiService,
    OpenRouterService,
    QwenService,
    LLMService,
)


def run(argv):
    """
    Execute the chat workflow.

    Args:
        argv: Command line arguments, expected to contain the user query.
    """
    typed_query = argv[0]
    max_context = int(env_var("max_context"))
    max_tokens = int(env_var("max_tokens"))
    system_prompt = env_var("system_prompt")
    chat_file = f"{env_var('alfred_workflow_data')}/chat.json"
    pid_stream_file = f"{env_var('alfred_workflow_cache')}/pid.txt"
    stream_file = f"{env_var('alfred_workflow_cache')}/stream.txt"
    http_proxy = env_var("http_proxy")
    socks5_proxy = env_var("socks5_proxy")
    streaming_now = env_var("streaming_now") == "1"
    stream_marker = env_var("stream_marker") == "1"

    selected_llm_service = env_var("selected_llm_service")

    openai_api_endpoint = env_var("openai_api_endpoint")
    openai_api_key = env_var("openai_api_key")
    openai_model = env_var("openai_model")

    anthropic_api_endpoint = env_var("anthropic_api_endpoint")
    anthropic_api_key = env_var("anthropic_api_key")
    anthropic_model = env_var("anthropic_model")

    gemini_api_endpoint = env_var("gemini_api_endpoint")
    gemini_api_key = env_var("gemini_api_key")
    gemini_model = env_var("gemini_model")

    qwen_api_endpoint = env_var("qwen_api_endpoint")
    qwen_api_key = env_var("qwen_api_key")
    qwen_model = env_var("qwen_model")

    ollama_api_endpoint = env_var("ollama_api_endpoint")
    ollama_model = env_var("ollama_model")

    deepseek_api_endpoint = env_var("deepseek_api_endpoint")
    deepseek_api_key = env_var("deepseek_api_key")
    deepseek_model = env_var("deepseek_model")

    cerebras_api_endpoint = env_var("cerebras_api_endpoint")
    cerebras_api_key = env_var("cerebras_api_key")
    cerebras_model = env_var("cerebras_model")

    openrouter_api_endpoint = env_var("openrouter_api_endpoint")
    openrouter_api_key = env_var("openrouter_api_key")
    openrouter_model = env_var("openrouter_model")

    llm_service: Optional[LLMService] = None
    if selected_llm_service == "openai":
        llm_service = OpenaiService(
            openai_api_endpoint, openai_api_key, openai_model, http_proxy, socks5_proxy
        )
    elif selected_llm_service == "anthropic":
        llm_service = AnthropicService(
            anthropic_api_endpoint,
            anthropic_api_key,
            anthropic_model,
            http_proxy,
            socks5_proxy,
        )
    elif selected_llm_service == "gemini":
        llm_service = GeminiService(
            gemini_api_endpoint, gemini_api_key, gemini_model, http_proxy, socks5_proxy
        )
    elif selected_llm_service == "qwen":
        llm_service = QwenService(
            qwen_api_endpoint, qwen_api_key, qwen_model, http_proxy, socks5_proxy
        )
    elif selected_llm_service == "ollama":
        llm_service = OllamaService(
            ollama_api_endpoint, ollama_model, http_proxy, socks5_proxy
        )
    elif selected_llm_service == "deepseek":
        llm_service = DeepseekService(
            deepseek_api_endpoint,
            deepseek_api_key,
            deepseek_model,
            http_proxy,
            socks5_proxy,
        )
    elif selected_llm_service == "cerebras":
        llm_service = CerebrasService(
            cerebras_api_endpoint,
            cerebras_api_key,
            cerebras_model,
            http_proxy,
            socks5_proxy,
        )
    elif selected_llm_service == "openrouter":
        llm_service = OpenRouterService(
            openrouter_api_endpoint,
            openrouter_api_key,
            openrouter_model,
            http_proxy,
            socks5_proxy,
        )

    if llm_service is None:
        return json.dumps({"response": "Error: No valid LLM service selected."})

    if streaming_now:
        return llm_service.read_stream(
            stream_file, chat_file, pid_stream_file, stream_marker
        )

    previous_chat = read_chat(chat_file)

    if file_exists(stream_file):
        return json.dumps(
            {
                "rerun": 0.1,
                "variables": {"streaming_now": True, "stream_marker": True},
                "response": markdown_chat(previous_chat, True),
                "behaviour": {"scroll": "end"},
            }
        )

    if not typed_query:
        return json.dumps(
            {
                "response": markdown_chat(previous_chat, False),
                "behaviour": {"scroll": "end"},
            }
        )

    append_query = {"role": "user", "content": typed_query}
    ongoing_chat = previous_chat + [append_query]
    context_chat = ongoing_chat[-max_context:]

    llm_service.start_stream(
        max_tokens, system_prompt, context_chat, stream_file, pid_stream_file
    )

    append_chat(chat_file, append_query)

    return json.dumps(
        {
            "rerun": 0.1,
            "variables": {"streaming_now": True, "stream_marker": True},
            "response": markdown_chat(ongoing_chat),
        }
    )


if __name__ == "__main__":
    output = run(sys.argv[1:])
    print(output)
