from enum import Enum
from typing import List, Tuple

from src.socket_instance import emit_agent
from .ollama_client import Ollama
from .claude_client import Claude
from .openai_client import OpenAI
from .groq_client import Groq
from .gemini_client import Gemini
from .mistral_client import MistralAi

from src.state import AgentState

import tiktoken

from ..config import Config
from ..logger import Logger

TOKEN_USAGE = 0
TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")

logger = Logger(filename="devika_prompts.log")

ollama = Ollama()


class LLM:
    def __init__(self, model_id: str = None):
        self.model_id = model_id
        self.log_prompts = Config().get_logging_prompts()
        self.models = {
            "CLAUDE": [
                ("Claude 3 Opus", "claude-3-opus-20240229"),
                ("Claude 3 Sonnet", "claude-3-sonnet-20240229"),
                ("Claude 3 Haiku", "claude-3-haiku-20240307"),
            ],
            "OPENAI": [
                ("GPT-4 Turbo", "gpt-4-0125-preview"),
                ("GPT-3.5", "gpt-3.5-turbo-0125"),
            ],
            "GOOGLE": [
                ("Gemini 1.0 Pro", "gemini-pro"),
            ],
            "MISTRAL": [
                ("Mistral 7b", "open-mistral-7b"),
                ("Mistral 8x7b", "open-mixtral-8x7b"),
                ("Mistral Medium", "mistral-medium-latest"),
                ("Mistral Small", "mistral-small-latest"),
                ("Mistral Large", "mistral-large-latest"),
            ],
            "OLLAMA_MODELS": [],
        }
        if ollama:
            self.models["OLLAMA_MODELS"] = [
                (model["name"].split(":")[0], model["name"])
                for model in ollama.list_models()
            ]

    def list_models(self) -> dict:
        return self.models

    def model_id_to_enum_mapping(self) -> dict:
        mapping = {}
        for enum_name, models in self.models.items():
            for model_name, model_id in models:
                mapping[model_id] = enum_name
        return mapping

    def update_global_token_usage(self, string: str, project_name: str):
        global TOKEN_USAGE
        TOKEN_USAGE += len(TIKTOKEN_ENC.encode(string))
        emit_agent("tokens", {"token_usage": TOKEN_USAGE})
        print(f"Token usage: {TOKEN_USAGE}")
        AgentState().update_token_usage(project_name, TOKEN_USAGE)

    def inference(self, prompt: str, project_name: str) -> str:
        self.update_global_token_usage(prompt, project_name)

        model = self.model_id_to_enum_mapping()[self.model_id]

        if self.log_prompts:
            logger.debug(f"Prompt ({model}): --> {prompt}")

        if model == "OLLAMA_MODELS":
            response = Ollama().inference(self.model_id, prompt).strip()
        elif "CLAUDE" in str(model):
            response = Claude().inference(self.model_id, prompt).strip()
        elif "GPT" in str(model):
            response = OpenAI().inference(self.model_id, prompt).strip()
        else:
            raise ValueError(f"Model {model} not supported")

        self.update_global_token_usage(response, project_name)

        return response
