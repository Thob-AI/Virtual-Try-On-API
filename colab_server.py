import os
import subprocess
import time
import threading
from IPython.display import HTML, display, clear_output
import ipywidgets as widgets

def setup_ui(ngrok_url):
    clear_output(wait=True)
    html_content = f"""
    <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style="margin-top: 0; color: #4a4a4a;">Virtual Try-On API Service</h2>
        <p><b>Status:</b> <span style="color: green;">Running</span></p>
        <p><b>Public URL:</b> <a href="{ngrok_url}" target="_blank">{ngrok_url}</a></p>
        <p><b>API Documentation:</b> <a href="{ngrok_url}/docs" target="_blank">{ngrok_url}/docs</a></p>
        <p><b>Web Interface:</b> <a href="{ngrok_url}/" target="_blank">{ngrok_url}/</a></p>
        <hr>
        <div>
            <h3>Available LoRA Models</h3>
            <ul>
                {get_lora_models_html()}
            </ul>
        </div>
    </div>
    """
    display(HTML(html_content))

def get_lora_models_html():
    from app.config import settings
    lora_html = ""
    try:
        lora_files = [f for f in os.listdir(settings.LORA_DIR) 
                     if f.endswith(('.pt', '.safetensors', '.ckpt'))]
        lora_html = "".join([f'<li>{f}</li>' for f in lora_files]) if lora_files else '<li>No LoRA models found</li>'
    except Exception as e:
        lora_html = f'<li>Error listing LoRAs: {str(e)}</li>'
    return lora_html

def start_server():
    subprocess.run("uvicorn app.main:app --host 0.0.0.0 --port 8000", shell=True)

def main():
    if not os.path.exists("app/main.py"):
        print("Error: app/main.py not found. Run from project root!")
        return

    # Install required packages
    subprocess.run("pip install pyngrok fastapi uvicorn python-multipart", shell=True)
    
    # Get secrets
    try:
        from google.colab import userdata
        ngrok_token = userdata.get("NGROK_TOKEN")
        hf_token = userdata.get("HUGGINGFACE_TOKEN")
        os.environ["HUGGINGFACE_TOKEN"] = hf_token
    except Exception as e:
        print(f"Error getting secrets: {str(e)}")
        return

    # Start server thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(5)  # Wait for server startup

    # Start ngrok
    from pyngrok import ngrok
    ngrok.set_auth_token(ngrok_token)
    public_url = ngrok.connect(8000).public_url

    # Display UI
    setup_ui(public_url)

    # Keep alive
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        ngrok.kill()
        print("Server stopped")

if __name__ == "__main__":
    main()