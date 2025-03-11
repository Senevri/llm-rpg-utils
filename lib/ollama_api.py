# Python script that communicates with ollamaimport requests
import json
from pprint import pformat
import requests

try:
    from lib.custom_logger import get_custom_logger
except ImportError:
    from custom_logger import get_custom_logger

logger = get_custom_logger(__file__, __name__, True, False, True)


class OllamaAPI:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def generate(self, model, prompt, stream=False):
        url = f"{self.base_url}/api/generate"
        headers = {"Content-Type": "application/json"}
        data = {"model": model, "prompt": prompt, "stream": stream}

        response = requests.post(url, headers=headers, data=json.dumps(data), stream=stream)
        response.raise_for_status()

        if stream:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    json_data = json.loads(decoded_line)
                    yield json_data
        else:
            return response.json()

    def _combine_responses(self, responses):
        full_response = []
        for response in responses:
            full_response.append(response["response"])
        return full_response

    def chat(self, model, messages, stream=False):
        """
        Responses are in markdown format
        """
        if isinstance(messages, str):
            messages = [messages]
        for message in messages:
            full_response = []
            responses = self.generate(model, message, stream)
            # logger.debug(list(responses))
            full_response = self._combine_responses(responses)
            yield (message, "".join(full_response))

    def list_models(self):
        url = f"{self.base_url}/api/tags"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def show_model_info(self, model):
        url = f"{self.base_url}/api/show"
        headers = {"Content-Type": "application/json"}
        data = {"name": model}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json


if __name__ == "__main__":
    api = OllamaAPI("http://192.168.1.109:11434")
    result = api.list_models()
    for model in result["models"]:
        logger.info(model["name"])
    msg = "give me a function that generates fibonacci sequence in python"
    responses = api.chat("deepseek-coder:6.7b", msg, stream=True)
    for response in responses:
        logger.info(response)

    # logger.info(pformat(result))
