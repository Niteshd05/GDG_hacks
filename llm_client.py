import openai
import anthropic
import requests
from groq import Groq
import google.genai as genai
import config
import time
import logging

logger = logging.getLogger(__name__)

def get_provider_delay(provider):
    """Get the configured delay for a specific provider."""
    delays = {
        "groq": config.GROQ_DELAY_SECONDS,
        "ollama": config.OLLAMA_DELAY_SECONDS,
        "openai": config.OPENAI_DELAY_SECONDS,
        "anthropic": config.ANTHROPIC_DELAY_SECONDS,
    }
    return delays.get(provider.lower(), config.REQUEST_DELAY_SECONDS)

def call_llm(model_spec, prompt, system_prompt=None):
    """
    Call an LLM with the given prompt.
    model_spec format: "provider/model_name"
    Supported providers: openai, anthropic, groq, ollama
    """
    provider, model_name = model_spec.split("/", 1)
    logger.info(f"🤖 Calling {provider}/{model_name} (prompt length: {len(prompt)} chars)")
    
    # Apply provider-specific delay before making request
    delay = get_provider_delay(provider)
    if delay > 0:
        logger.debug(f"⏱️  Applying {delay}s delay for {provider}")
        time.sleep(delay)
    
    for attempt in range(config.MAX_RETRIES):
        try:
            # Note: Delay is applied before the retry loop, not here
            
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
                logger.info(f"→ Using Ollama endpoint: {ollama_url}")
                
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
                    timeout=180  # Increased timeout for judge synthesis
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ Ollama returned status {response.status_code}: {response.text}")
                    response.raise_for_status()
                
                result = response.json()
                
                # Check if response contains error
                if "error" in result:
                    raise Exception(f"Ollama error: {result['error']}")
                
                response_text = result.get("response", "")
                if not response_text:
                    raise Exception("Ollama returned empty response")
                    
                return response_text
            
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
            error_str = str(e)
            logger.error(f"❌ LLM call error for {provider}/{model_name}: {error_str}")
            
            # Check for rate limiting errors (429 status code)
            if "429" in error_str and "rate" in error_str.lower():
                wait_time = (config.RETRY_BACKOFF_FACTOR ** attempt) * 2  # Exponential backoff
                logger.warning(f"⚠️ Rate limit detected. Retrying in {wait_time}s... (attempt {attempt + 1}/{config.MAX_RETRIES})")
                time.sleep(wait_time)
                if attempt == config.MAX_RETRIES - 1:
                    logger.error(f"❌ Max retries exceeded for {provider}")
                    raise
            else:
                # For non-rate-limit errors, raise immediately
                raise
