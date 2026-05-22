import time
from openai import OpenAI
from config import Config


class LLMClient:
    def __init__(self):
        self._client = OpenAI(api_key=Config.API_KEY, base_url=Config.BASE_URL)

    def chat_completion(self, messages: list[dict], **kwargs) -> str:
        model = kwargs.get("model", Config.MODEL)
        temperature = kwargs.get("temperature", Config.TEMPERATURE)
        max_tokens = kwargs.get("max_tokens", Config.MAX_TOKENS)

        last_error = None
        for attempt in range(Config.MAX_RETRIES):
            try:
                extra_body = {}
                if Config.THINKING_LEVEL:
                    extra_body["thinking"] = {"type": Config.THINKING_LEVEL}

                response = self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_body=extra_body if extra_body else None,
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(Config.RETRY_DELAY * (attempt + 1))

        raise RuntimeError(f"LLM call failed after {Config.MAX_RETRIES} retries: {last_error}")
