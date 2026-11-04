""" Commonly used LLM configurations for convenience. """

import uuid

from llm.openai_llm import LLMConfig
from utility.environment_variables import get_env_variable

"""
Example LLM configuration for Ollama models:
ollama_model_config = LLMConfig(
    api_key="supersecret", # dummy value, Ollama does not require an API key
    base_url="http://localhost:11434/v1",
    model_name="model_name"
)

Example LLM configuration for OpenCode models:
opencode_model_config = LLMConfig(
    api_key=get_env_variable("OPENCODE_API_KEY"),
    base_url="https://opencode.ai/zen/v1",
    model_name="model_name"
)
For this to work, you need to set the OPENCODE_API_KEY environment variable in your .env file.
"""

# OpenCode Go requires clients to identify themselves with their
# own User-Agent and to send a stable per-conversation session ID
qwen3_7_plus_config = LLMConfig(
    api_key=get_env_variable("OPENCODE_GO_API_KEY"),
    base_url="https://opencode.ai/zen/go/v1/",
    model_name="qwen3.7-plus",
    timeout=900,
    extra_headers={
        "User-Agent": "my-coding-agent/1.0",
        "x-opencode-session": str(uuid.uuid4()),
    },
    disable_thinking_for_tool_calls=True # otherwise the model will reject tool_choice="required"
)