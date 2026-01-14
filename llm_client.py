import openai
import anthropic
import requests
from groq import Groq
import google.genai as genai
import config
import time
import logging

logger = logging.getLogger(__name__)

def call_llm(model_spec, prompt, system_prompt=None):
    """
    Call an LLM with the given prompt.
    model_spec format: "provider/model_name"
    Supported providers: openai, anthropic, groq, ollama
    """
    provider, model_name = model_spec.split("/", 1)
    
    for attempt in range(config.MAX_RETRIES):
        try:
            # Add delay between requests to avoid rate limiting
            if attempt == 0:
                time.sleep(config.REQUEST_DELAY_SECONDS)
            
            if provider == "openai":
                # Use OpenRouter by default, fall back to OpenAI if no OpenRouter key
                if config.OPENROUTER_API_KEY:
                    client = openai.OpenAI(
                        api_key=config.OPENROUTER_API_KEY,
                        base_url="https://openrouter.io/api/v1",
                        default_headers={"HTTP-Referer": "http://localhost"}
                    )
                else:
                    client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
                
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.7
                )
                return response.choices[0].message.content
            
            elif provider == "anthropic":
                client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
                
                response = client.messages.create(
                    model=model_name,
                    max_tokens=4096,
                    system=system_prompt if system_prompt else "",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                return response.content[0].text
            
            elif provider == "groq":
                client = Groq(api_key=config.GROQ_API_KEY)
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=4096
                )
                return response.choices[0].message.content
            
            elif provider == "ollama":
                # Route to local or remote based on model
                # Local models: qwen2.5:7B (judge)
                # Remote models: llama3:latest (debate agents)
                if model_name in ["qwen2.5:7B"]:
                    ollama_url = config.OLLAMA_LOCAL_URL
                else:
                    ollama_url = config.OLLAMA_REMOTE_URL
                
                # Use native /api/generate endpoint
                full_prompt = ""
                if system_prompt:
                    full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
                else:
                    full_prompt = prompt
                
                response = requests.post(
                    f"{ollama_url}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": full_prompt,
                        "stream": False,
                        "temperature": 0.7
                    },
                    timeout=120
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("response", "")
                return response.json()["response"]
            
            elif provider == "gemini":
                client = genai.Client(api_key=config.GEMINI_API_KEY)
                
                # Combine system and user messages
                full_text = ""
                if system_prompt:
                    full_text = f"System: {system_prompt}\n\nUser: {prompt}"
                else:
                    full_text = prompt
                
                response = client.models.generate_content(
                    model=f"models/{model_name}",
                    contents=full_text,
                    config=genai.types.GenerateContentConfig(
                        temperature=0.7,
                        max_output_tokens=4096
                    )
                )
                return response.text
            
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except Exception as e:
            # Check for rate limiting errors
            if "429" in str(e) or "rate" in str(e).lower():
                wait_time = (config.RETRY_BACKOFF_FACTOR ** attempt) * 2  # Exponential backoff
                logger.warning(f"⚠️ Rate limit hit for {provider}. Retrying in {wait_time}s... (attempt {attempt + 1}/{config.MAX_RETRIES})")
                time.sleep(wait_time)
                if attempt == config.MAX_RETRIES - 1:
                    logger.error(f"❌ Max retries exceeded for {provider}")
                    raise
            else:
                # For non-rate-limit errors, raise immediately
                logger.error(f"❌ LLM call failed for {provider}: {e}")
                raise
