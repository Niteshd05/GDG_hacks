import openai
import anthropic
import requests
from groq import Groq
import google.genai as genai
import config
import time
import logging

logger = logging.getLogger(__name__)


# -------------------------------
# Provider Delay Handling
# -------------------------------
def get_provider_delay(provider):
    delays = {
        "groq": config.GROQ_DELAY_SECONDS,
        "ollama": config.OLLAMA_DELAY_SECONDS,
        "openai": config.OPENAI_DELAY_SECONDS,
        "anthropic": config.ANTHROPIC_DELAY_SECONDS,
    }
    return delays.get(provider.lower(), config.REQUEST_DELAY_SECONDS)


# -------------------------------
# Main LLM Call Function
# -------------------------------
def call_llm(model_spec, prompt, system_prompt=None):
    """
    model_spec format: provider/model_name
    Supported providers:
    openai, anthropic, groq, ollama, gemini
    """

    provider, model_name = model_spec.split("/", 1)
    logger.info(f"🤖 Calling {provider}/{model_name} (prompt length: {len(prompt)} chars)")

    delay = get_provider_delay(provider)
    if delay > 0:
        time.sleep(delay)

    start_time = time.time()

    for attempt in range(config.MAX_RETRIES):
        try:

            # ==========================================================
            # OPENAI / OPENROUTER
            # ==========================================================
            if provider == "openai":
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


            # ==========================================================
            # ANTHROPIC
            # ==========================================================
            elif provider == "anthropic":
                client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

                response = client.messages.create(
                    model=model_name,
                    max_tokens=4096,
                    system=system_prompt or "",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                return response.content[0].text


            # ==========================================================
            # GROQ
            # ==========================================================
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


            # ==========================================================
            # OLLAMA (MODEL-AWARE ROUTING)
            # ==========================================================
            elif provider == "ollama":

                # -------- Routing --------
                LOCAL_MODELS = {
                    "qwen2.5:7b",
                }

                is_local = model_name.lower() in LOCAL_MODELS
                ollama_url = (
                    config.OLLAMA_LOCAL_URL
                    if is_local
                    else config.OLLAMA_REMOTE_URL
                )

                endpoint_type = "LOCAL" if is_local else "REMOTE"
                logger.info(f"🔀 ROUTING: {endpoint_type} [{ollama_url}] for {model_name}")

                # ======================================================
                # DeepSeek-R1 → /api/chat (CRITICAL FIX)
                # ======================================================
                if "deepseek-r1" in model_name.lower():
                    messages = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.append({"role": "user", "content": prompt})

                    response = requests.post(
                        f"{ollama_url}/api/chat",
                        json={
                            "model": model_name,
                            "messages": messages,
                            "stream": False,
                            "options": {
                                "num_ctx": 8192,
                                "temperature": 0.7
                            }
                        },
                        timeout=180
                    )

                    response.raise_for_status()
                    result = response.json()

                    response_text = result.get("message", {}).get("content", "").strip()

                # ======================================================
                # Other Ollama models → /api/generate
                # ======================================================
                else:
                    response = requests.post(
                        f"{ollama_url}/api/generate",
                        json={
                            "model": model_name,
                            "prompt": prompt,
                            "stream": False,
                            "temperature": 0.7,
                            "options": {
                                "num_ctx": 8192,
                                "num_predict": 4096
                            }
                        },
                        timeout=180
                    )

                    response.raise_for_status()
                    result = response.json()
                    response_text = result.get("response", "").strip()

                # -------- Empty Response Safety Retry --------
                if not response_text:
                    if attempt < config.MAX_RETRIES - 1:
                        logger.warning("⚠️ Empty response detected, retrying once...")
                        time.sleep(2)
                        continue
                    raise Exception("Ollama returned empty response")

                elapsed = time.time() - start_time
                logger.info(f"✓ Ollama response received in {elapsed:.1f}s")
                return response_text


            # ==========================================================
            # GEMINI
            # ==========================================================
            elif provider == "gemini":
                client = genai.Client(api_key=config.GEMINI_API_KEY)

                full_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

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
            logger.error(f"❌ Error calling {provider}/{model_name}: {e}")

            if "429" in str(e):
                wait = (config.RETRY_BACKOFF_FACTOR ** attempt) * 2
                logger.warning(f"⏳ Rate limit hit, retrying in {wait}s...")
                time.sleep(wait)
                continue

            raise