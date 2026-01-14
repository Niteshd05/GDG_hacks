import openai
import anthropic
import requests
from groq import Groq
import config

def call_llm(model_spec, prompt, system_prompt=None):
    """
    Call an LLM with the given prompt.
    model_spec format: "provider/model_name"
    Supported providers: openai, anthropic, groq, ollama
    """
    provider, model_name = model_spec.split("/", 1)
    
    if provider == "openai":
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
        # Ollama API endpoint
        ollama_url = config.OLLAMA_BASE_URL or "http://127.0.0.1:11434"
        
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
                "options": {"temperature": 0.7}
            }
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    
    else:
        raise ValueError(f"Unknown provider: {provider}")
