import os
import subprocess
import time
import threading
import psutil
from IPython.display import HTML, display, clear_output
from pyngrok import ngrok, conf

def kill_process_on_port(port=8000):
    """Kill any processes using the specified port"""
    for proc in psutil.process_iter():
        try:
            for conns in proc.connections(kind='inet'):
                if conns.laddr.port == port:
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def run_in_colab():
    # Cleanup existing processes
    kill_process_on_port()
    
    # Install dependencies
    subprocess.run("pip install pyngrok psutil fastapi==0.104.1 uvicorn==0.23.2 python-multipart", 
                  shell=True, check=True)

    # Get secrets
    from google.colab import userdata
    try:
        ngrok_token = userdata.get("ngrok")
        hf_token = userdata.get("HF_TOKEN")
        os.environ["HUGGINGFACE_TOKEN"] = hf_token or ""
    except Exception as e:
        print(f"⚠️ Secret Error: {str(e)}")
        return

    # Start server
    def start_server():
        try:
            with open("server.log", "w") as log_file:
                subprocess.Popen(
                    "uvicorn app.main:app --host 0.0.0.0 --port 8000",
                    shell=True,
                    stdout=log_file,
                    stderr=subprocess.STDOUT
                )
        except Exception as e:
            print(f"Server start failed: {str(e)}")

    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(8)

    # Configure ngrok
    conf.get_default().region = "eu"
    ngrok.set_auth_token(ngrok_token)
    
    try:
        public_url = ngrok.connect(8000, bind_tls=True).public_url
        display(HTML(f"""<div style="padding:20px; background:#f5f5f5;">
            <h3>Service Running 🚀</h3>
            <p>Access URL: <a href="{public_url}" target="_blank">{public_url}</a></p>
        </div>"""))
        while True: time.sleep(1)
    except Exception as e:
        print(f"Ngrok error: {str(e)}")

if __name__ == "__main__" and 'google.colab' in str(get_ipython()):
    run_in_colab()