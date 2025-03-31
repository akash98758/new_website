import httpx
import os
from typing import Dict

class OpenRouterService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"

    async def generate_code(self, prompt: str, framework: str = "react") -> Dict:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com",  # Required by OpenRouter
                "X-Title": "AI Code Generator"  # Required by OpenRouter
            }
            
            payload = {
                "model": "open-r1/olympiccoder-32b:free",
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are an expert {framework} developer. Generate clean, efficient code with no explanations."
                    },
                    {
                        "role": "user",
                        "content": f"Create a complete {framework} component that: {prompt}\n\nReturn ONLY the code with no additional text."
                    }
                ]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": response.text
                    }
                
                code = response.json()["choices"][0]["message"]["content"]
                return {
                    "success": True,
                    "code": code,
                    "files": {
                        "/src/App.js": code
                    }
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }