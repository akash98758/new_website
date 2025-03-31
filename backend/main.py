from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from typing import Optional, Dict
from gemini_service import GeminiService
from openrouter_service import OpenRouterService

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Config:
    CODESANDBOX_API_KEY = os.getenv("CODESANDBOX_API_KEY")
    AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")  # gemini or openrouter

class CodeGenerationRequest(BaseModel):
    prompt: str
    framework: str = "react"
    language: str = "javascript"
    ai_provider: str = "gemini"

class SandboxPreviewResponse(BaseModel):
    sandbox_id: str
    preview_url: str
    status: str

@app.post("/generate-code", response_model=SandboxPreviewResponse)
async def generate_code(request: CodeGenerationRequest):
    try:
        # Initialize the selected AI service
        if request.ai_provider.lower() == "gemini":
            ai_service = GeminiService()
        else:
            ai_service = OpenRouterService()
        
        # Generate code
        ai_code = await ai_service.generate_code(request.prompt, request.framework)
        if not ai_code.get("success"):
            raise HTTPException(status_code=400, detail=ai_code.get("error", "AI generation failed"))
        
        # Create sandbox
        sandbox_data = await create_or_update_sandbox(ai_code)
        
        return {
            "sandbox_id": sandbox_data["sandbox_id"],
            "preview_url": sandbox_data["preview_url"],
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def create_or_update_sandbox(code_data: Dict) -> Dict:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.CODESANDBOX_API_KEY}"
    }
    
    # Prepare sandbox files structure
    files = {
        "package.json": {
            "content": {
                "name": "ai-generated-app",
                "version": "1.0.0",
                "main": "src/App.js",
                "scripts": {
                    "start": "react-scripts start",
                    "build": "react-scripts build"
                },
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-scripts": "5.0.1"
                }
            }
        },
        "src/App.js": {
            "content": code_data.get("code", "// Generated code will appear here")
        }
    }
    
    # Add additional files if provided by AI
    for file_path, content in code_data.get("files", {}).items():
        files[file_path] = {"content": content}
    
    payload = {
        "files": files,
        "template": "create-react-app"
    }
    
    # Create new sandbox
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://codesandbox.io/api/v1/sandboxes/define",
            json=payload,
            headers=headers,
            params={"json": 1},
            timeout=30.0
        )
        
        if response.status_code != 200:
            raise Exception(f"CodeSandbox API error: {response.text}")
        
        sandbox_id = response.json()["sandbox_id"]
        
        return {
            "sandbox_id": sandbox_id,
            "preview_url": f"https://{sandbox_id}.csb.app"
        }

@app.get("/sandbox/{sandbox_id}")
async def get_sandbox_status(sandbox_id: str):
    headers = {
        "Authorization": f"Bearer {Config.CODESANDBOX_API_KEY}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://codesandbox.io/api/v1/sandboxes/{sandbox_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        return response.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)