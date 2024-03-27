import httpx
from ollama import Client
from src.config import Config

from src.logger import Logger
from src.config import Config
from src.exceptions import ServerNotRunning

log = Logger()

client = Client(host=Config().get_ollama_api_endpoint())


class Ollama:
    def __init__(self):
        try:
            self.client = ollama.Client(host=Config().get_ollama_api_endpoint())
            log.info("Ollama available")
        except:
            self.client = None
            log.warning("Ollama not available")
            log.warning(
                "run ollama server to use ollama models otherwise use other models"
            )

    def list_models(self) -> list[dict]:
        if self.client is None:
            raise ServerNotRunning("Ollama not available.")

        models = self.client.list()["models"]
        return models

    def inference(self, model_id: str, prompt: str) -> str:
        if self.client is None:
            raise ServerNotRunning("Ollama not available.")

        response = self.client.generate(model=model_id, prompt=prompt.strip())
        return response["response"]
