"""LLM Client for agent intelligence"""
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
import anthropic
from openai import OpenAI

logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM client"""
    provider: str = "anthropic"  # anthropic, openai
    model: str = "claude-3-7-sonnet-20250219"  # Default to Claude 3.7 Sonnet
    temperature: float = 0.7
    max_tokens: int = 4096
    api_key: Optional[str] = None

class LLMClient:
    """Unified LLM client supporting multiple providers"""
    
    SUPPORTED_MODELS = {
        "anthropic": [
            "claude-3-7-sonnet-20250219",  # Claude 3.7 Sonnet
            "claude-3-5-sonnet-20241022",  # Claude 3.5 Sonnet
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307"
        ],
        "openai": [
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
    }
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self._validate_config()
        self._initialize_client()
    
    def _validate_config(self):
        """Validate configuration and set API keys"""
        # Get API key from config or environment
        if self.config.provider == "anthropic":
            self.config.api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
            if not self.config.api_key:
                logger.warning("No Anthropic API key found. Set ANTHROPIC_API_KEY environment variable.")
        elif self.config.provider == "openai":
            self.config.api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
            if not self.config.api_key:
                logger.warning("No OpenAI API key found. Set OPENAI_API_KEY environment variable.")
        
        # Validate model selection
        if self.config.provider in self.SUPPORTED_MODELS:
            if self.config.model not in self.SUPPORTED_MODELS[self.config.provider]:
                default_model = self.SUPPORTED_MODELS[self.config.provider][0]
                logger.warning(f"Model {self.config.model} not supported for {self.config.provider}. Using {default_model}")
                self.config.model = default_model
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client"""
        if not self.config.api_key:
            self.client = None
            return
        
        try:
            if self.config.provider == "anthropic":
                self.client = anthropic.Anthropic(api_key=self.config.api_key)
            elif self.config.provider == "openai":
                self.client = OpenAI(api_key=self.config.api_key)
            else:
                self.client = None
                logger.error(f"Unsupported provider: {self.config.provider}")
        except Exception as e:
            logger.error(f"Failed to initialize {self.config.provider} client: {e}")
            self.client = None
    
    async def generate(self, 
                      prompt: str, 
                      system_prompt: Optional[str] = None,
                      temperature: Optional[float] = None,
                      max_tokens: Optional[int] = None) -> Optional[str]:
        """Generate text using the configured LLM"""
        if not self.client:
            logger.error("LLM client not initialized. Please check API key configuration.")
            return None
        
        temp = temperature or self.config.temperature
        max_tok = max_tokens or self.config.max_tokens
        
        try:
            if self.config.provider == "anthropic":
                messages = [{"role": "user", "content": prompt}]
                if system_prompt:
                    response = self.client.messages.create(
                        model=self.config.model,
                        system=system_prompt,
                        messages=messages,
                        temperature=temp,
                        max_tokens=max_tok
                    )
                else:
                    response = self.client.messages.create(
                        model=self.config.model,
                        messages=messages,
                        temperature=temp,
                        max_tokens=max_tok
                    )
                return response.content[0].text
            
            elif self.config.provider == "openai":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=max_tok
                )
                return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return None
    
    async def generate_json(self, 
                          prompt: str, 
                          system_prompt: Optional[str] = None,
                          schema: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Generate JSON output from the LLM"""
        import json
        
        json_prompt = prompt
        if schema:
            json_prompt += f"\n\nPlease respond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        else:
            json_prompt += "\n\nPlease respond with valid JSON only."
        
        response = await self.generate(json_prompt, system_prompt)
        if not response:
            return None
        
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if LLM client is available"""
        return self.client is not None