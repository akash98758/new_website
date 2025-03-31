import google.generativeai as genai
import os
from typing import Dict

class GeminiService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')

    async def generate_code(self, prompt: str, framework: str = "react") -> Dict:
        try:
            full_prompt = f"""
            Generate a complete {framework} component based on this description:
            {prompt}
            
            Requirements:
            - Use modern {framework} best practices
            - Include all necessary imports
            - Add basic styling
            - Export the component
            - Return ONLY the code with no additional explanations
            """
            
            response = await self.model.generate_content_async(full_prompt)
            return {
                "success": True,
                "code": response.text,
                "files": {
                    "/src/App.js": response.text
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }