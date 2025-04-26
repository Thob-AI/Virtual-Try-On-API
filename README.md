# Virtual Try-On API

A FastAPI-based service for generating clothing images and virtual try-on using AI models. This API integrates Stable Diffusion for clothing generation and [OOTDiffusion](https://github.com/levihsu/OOTDiffusion/tree/main) for the virtual try-on functionality.

## Overview

This project provides a web API for:
1. Generating realistic clothing images based on text prompts
2. Applying generated clothes to a model image using virtual try-on technology

The system is designed to be deployed both locally and on Google Colab with ngrok tunneling.

## Project Structure

```
├── OOTDiffusion/       # OOTDiffusion repository (cloned during setup)
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py   # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── clothing_generator.py  # Stable Diffusion generator
│   │   └── virtual_tryon.py       # OOTDiffusion integration
│   ├── utils/
│   │   ├── __init__.py
│   │   └── image_utils.py         # Image processing utilities
│   ├── __init__.py
│   ├── config.py                  # Configuration settings
│   └── main.py                    # FastAPI app setup
├── envs/
│   ├── sd_env/                    # Environment for Stable Diffusion
│   └── ootd_env/                  # Environment for OOTDiffusion
├── models/
│   ├── lora/                      # LoRA models for clothing generation
│   └── ootd/                      # Virtual try-on models
├── outputs/                       # Generated images stored here
├── static/
│   └── images/
│       └── default_model.jpg      # Default model image
├── templates/
│   └── index.html                 # Frontend interface
├── uploads/                       # Temporary storage for uploads
├── LICENSE
├── README.md
├── colab_server.py                # Google Colab integration
├── requirements_ootd.txt          # Requirements for OOTDiffusion
├── requirements_sdxl.txt          # Requirements for Stable Diffusion
├── server.log                      # Server logs
└── setup_models.py                # Setup script
```

## Prerequisites

- Python 3.8 or higher
- CUDA-compatible GPU with at least 8GB VRAM
- Git LFS (for downloading model checkpoints)

## Installation

### Option 1: Local Setup

1. Clone this repository:

```bash
git clone https://github.com/yourusername/virtual-tryon-api.git
cd virtual-tryon-api
```

2. Run the setup script to create environments and download models:

```bash
python setup_models.py
```

This script will:
- Create virtual environments for Stable Diffusion and OOTDiffusion
- Clone the OOTDiffusion repository
- Download required model checkpoints
- Fix any potential issues with dependencies

3. Start the API server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Access the API at: http://localhost:8000

### Option 2: Google Colab Deployment

1. Upload the project files to Google Drive

2. Create a new Colab notebook and mount your Google Drive:

```python
from google.colab import drive
drive.mount('/content/drive')
```

3. Navigate to your project directory:

```python
%cd /content/drive/MyDrive/path/to/virtual-tryon-api
```

4. Run the setup script:

```python
!python setup_models.py
```

5. Add your ngrok authentication token as Colab secret:
   - Go to ngrok dashboard to get your token
   - In Colab, add a new secret named "ngrok" with your token value
   - Optionally add your HuggingFace token as "HF_TOKEN"

6. Run the Colab server script in a notebook cell:

```python
import colab_server
colab_server.run_in_colab()
```

7. Click on the generated URL to access the web interface

## API Usage

### Generate Clothing Image

```
POST /api/generate-clothing
```

Form parameters:
- `prompt`: Text description of the clothing (required)
- `lora_scale`: LoRA adaptation scale (default: 0.7)
- `steps`: Number of diffusion steps (default: 30)
- `guidance`: Guidance scale (default: 7.5)
- `seed`: Random seed (default: 42)

Response:
```json
{
  "request_id": "unique_id",
  "clothing_url": "/api/images/unique_id/clothing.png"
}
```

### Virtual Try-On

```
POST /api/virtual-tryon
```

Form parameters:
- `clothing_url`: URL from previous generation (required)
- `category`: Clothing category (0=upper, 1=lower, 2=dress)

Response:
```json
{
  "result_url": "/api/images/unique_id/result_out_0.png"
}
```

### Get Image

```
GET /api/images/{request_id}/{filename}
```

Returns the generated image file.

## Examples

### Generate a clothing image and try it on

```python
import requests

# Generate clothing
response = requests.post(
    "http://localhost:8000/api/generate-clothing",
    data={
        "prompt": "blue t-shirt with pattern, on plain white background"
    }
)
clothing_data = response.json()

# Apply virtual try-on
tryon_response = requests.post(
    "http://localhost:8000/api/virtual-tryon",
    data={
        "clothing_url": clothing_data["clothing_url"],
        "category": 0  # Upper body
    }
)
result_data = tryon_response.json()

print(f"Result available at: {result_data['result_url']}")
```

## Troubleshooting

- **GPU Memory Issues**: Reduce batch size or resolution if you encounter CUDA out of memory errors
- **Missing Dependencies**: Make sure all requirements are installed in the correct environments
- **OOTDiffusion Errors**: Check that all checkpoints are properly downloaded and placed in the correct directories
- **Port Conflicts**: Use the `kill_process_on_port()` function in `colab_server.py` to free up port 8000
- **Path Issues**: Review the log files for any path-related errors and adjust the configuration as needed


## Citation

This project relies on OOTDiffusion. If you use this project in your research or application, please cite:

```
@inproceedings{hsu2023ootdiffusion,
  title={OOTDiffusion: Outfitting Fusion based Latent Diffusion for Controllable Virtual Try-on},
  author={Hsu, Wei-Chiu and Huang, Yihao and Ma, Yanrui and Li, Jiashuo and Liu, Ming-Yu and Lin, Yuting},
  booktitle={Proceedings of the IEEE/CVF International Conference on Computer Vision},
  year={2023}
}
```

This project uses the implementation from:
- https://github.com/levihsu/OOTDiffusion/tree/main