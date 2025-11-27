from typing import Generator
from loguru import logger
from config import settings
from openai import OpenAI




class OpenAILLM:
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo", base_url: str = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai not installed")
        
        if not settings.allow_cloud_models:
            raise PermissionError(
                "Cloud models are disabled. Enable in settings to use OpenAI."
            )
        
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.base_url = base_url or getattr(settings, 'openai_base_url', None)
        
        if self.base_url:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            logger.info(f"Using OpenAI-compatible API at: {self.base_url}")
        else:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("Using official OpenAI API")
        
        self.model = model
        logger.info(f"Using model: {self.model}")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream
        )
        
        if stream:
            return self._stream_response(response)
        else:
            return response.choices[0].message.content
    
    def _stream_response(self, response) -> Generator:
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


def get_llm(api_key: str = None) -> OpenAILLM:
    model = getattr(settings, 'openai_model', 'gpt-3.5-turbo')
    base_url = getattr(settings, 'openai_base_url', None)
    return OpenAILLM(api_key=api_key, model=model, base_url=base_url)
