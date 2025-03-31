class CodeGeneratorFrontend {
    constructor(backendUrl = "https://friendly-goldfish-ggrrg5j65jv2xg6-8000.app.github.dev/") {
      this.backendUrl = backendUrl;
    }
  
    async generateCode(prompt, framework, aiProvider) {
      try {
        const response = await fetch(`${this.backendUrl}/generate-code`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt,
            framework,
            ai_provider: aiProvider
          }),
        });
  
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || "Failed to generate code");
        }
  
        return await response.json();
      } catch (error) {
        console.error("Error generating code:", error);
        throw error;
      }
    }
  
    async getSandboxStatus(sandboxId) {
      try {
        const response = await fetch(`${this.backendUrl}/sandbox/${sandboxId}`);
  
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || "Failed to get sandbox status");
        }
  
        return await response.json();
      } catch (error) {
        console.error("Error getting sandbox status:", error);
        throw error;
      }
    }
  }
  
  document.addEventListener("DOMContentLoaded", () => {
    const codespaceUrl = window.location.host.includes('github.dev') ? 
      `https://${window.location.host.replace('github.dev', 'preview.app.github.dev')}` : 
      "http://localhost:8000";
    
    const codeGenerator = new CodeGeneratorFrontend(codespaceUrl);
    const generateBtn = document.getElementById("generate-btn");
    const promptInput = document.getElementById("code-prompt");
    const frameworkSelect = document.getElementById("framework");
    const aiProviderSelect = document.getElementById("ai-provider");
    const previewFrame = document.getElementById("preview-frame");
    const statusElement = document.getElementById("status");
  
    generateBtn.addEventListener("click", async () => {
      const prompt = promptInput.value.trim();
      const framework = frameworkSelect.value;
      const aiProvider = aiProviderSelect.value;
      
      if (!prompt) {
        updateStatus("Please enter a description of what you want to build", "error");
        return;
      }
  
      updateStatus("Generating code...", "info");
      generateBtn.disabled = true;
  
      try {
        const result = await codeGenerator.generateCode(prompt, framework, aiProvider);
        
        previewFrame.src = result.preview_url;
        updateStatus("Code generated successfully! Preview loading...", "success");
        
        // Check sandbox status periodically
        const checkStatus = async () => {
          try {
            const status = await codeGenerator.getSandboxStatus(result.sandbox_id);
            console.log("Sandbox status:", status);
            if (status.data?.sandbox?.isRunning) {
              updateStatus("Preview is ready!", "success");
            }
          } catch (error) {
            console.log("Status check error:", error);
          }
        };
        
        const statusInterval = setInterval(checkStatus, 5000);
        
        // Clean up interval when preview frame loads
        previewFrame.onload = () => {
          clearInterval(statusInterval);
          updateStatus("Preview loaded successfully!", "success");
        };
        
      } catch (error) {
        updateStatus(`Error: ${error.message}`, "error");
        console.error("Generation error:", error);
      } finally {
        generateBtn.disabled = false;
      }
    });
  
    function updateStatus(message, type = "info") {
      statusElement.textContent = message;
      statusElement.className = "status-message";
      if (type === "success") {
        statusElement.classList.add("success");
      } else if (type === "error") {
        statusElement.classList.add("error");
      }
    }
  });