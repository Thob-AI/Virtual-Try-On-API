# Virtual Try-On API

A FastAPI application that provides virtual try-on functionality using Stable Diffusion 2.1 (with optional LoRA support) for clothing generation and OOTDiffusion for virtual try-on.

## Overview

This API allows you to:
1. Generate clothing images from text prompts using Stable Diffusion 2.1
2. Apply LoRA fine-tuning to the clothing generation
3. Perform virtual try-on with OOTDiffusion
4. Combine both functionalities to generate clothing from a prompt and try it on a model

## Setup

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU
- Git LFS installed

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/virtual-tryon-api.git
cd virtual-tryon-api
```

2. Copy the requirements files:
```bash
# Copy requirements_sdxl.txt and requirements_ootd.txt to the project root
```

3. Run the setup script:
```bash
python setup_models.py
```

This script will:
- Create virtual environments for Stable Diffusion and OOTDiffusion
- Install the required dependencies
- Clone the OOTDiffusion repository and download necessary checkpoints
- Fix any potential import issues in the dependencies

4. (Optional) Add LoRA models:
```bash
# Place your LoRA models in the models/lora directory
cp your-clothing-lora.safetensors models/lora/
```

### Running the API

Start the FastAPI server:
```bash
source envs/sd_env/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000. You can access the API documentation at http://localhost:8000/docs.

## API Endpoints

### Generate Clothing

```
POST /api/generate-clothing
```

Generates a clothing image based on a text prompt using Stable Diffusion 2.1.

**Form Parameters:**
- `prompt` (string, required): Text description of the clothing to generate
- `lora_path` (string, optional): Path to LoRA weights file
- `lora_scale` (float, optional, default=0.7): Scale factor for LoRA weights
- `negative_prompt` (string, optional): Negative prompt to guide generation
- `steps` (int, optional, default=30): Number of diffusion steps
- `guidance` (float, optional, default=7.5): Guidance scale
- `seed` (int, optional, default=42): Random seed

**Response:**
```json
{
  "request_id": "uuid-string",
  "image_path": "/path/to/clothing.png",
  "image_url": "/api/images/uuid-string/clothing.png"
}
```

### Virtual Try-On

```
POST /api/virtual-tryon
```

Performs virtual try-on with either an uploaded clothing image or by generating one from a prompt.

**Form Parameters:**
- `clothing_image` (file, optional): Clothing image file to try on
- `model_image` (file, required): Person image to dress
- `prompt` (string, optional if clothing_image provided): Text description to generate clothing
- `lora_path` (string, optional): Path to LoRA weights for clothing generation
- `category` (int, optional, default=0): Garment category (0=upper, 1=lower, 2=dress)
- `sample_count` (int, optional, default=4): Number of samples to generate
- `scale` (float, optional, default=2.0): Scale factor for try-on

**Response:**
```json
{
  "request_id": "uuid-string",
  "result_path": "/path/to/result.png",
  "result_url": "/api/images/uuid-string/result.png",
  "model_url": "/api/images/uuid-string/model.png",
  "clothing_url": "/api/images/uuid-string/clothing.png"
}
```

### Get Generated Image

```
GET /api/images/{request_id}/{filename}
```

Retrieves a generated image by its request ID and filename.

**Path Parameters:**
- `request_id` (string, required): UUID of the request
- `filename` (string, required): Name of the file (e.g., "clothing.png", "result.png")

**Response:**
- The image file

## Examples

### Generate Clothing and Try It On

```python
import requests

# API endpoint
api_url = "http://localhost:8000/api"

# Step 1: Upload model image
with open("person.jpg", "rb") as f:
    model_file = {"model_image": f}
    
    # Additional parameters
    data = {
        "prompt": "a simple grey t-shirt, front view, plain, minimal, product photography",
        "category": 0,  # 0 for upper body clothing
        "sample_count": 4,
        "scale": 2.0
    }
    
    # Make the request
    response = requests.post(f"{api_url}/virtual-tryon", files=model_file, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Try-on result URL: {result['result_url']}")
        print(f"Generated clothing URL: {result['clothing_url']}")
    else:
        print(f"Error: {response.json()}")
```

## Deploying with Docker

A Dockerfile is provided to containerize the application. Build and run the Docker container:

```bash
# Build the Docker image
docker build -t virtual-tryon-api .

# Run the container
docker run -p 8000:8000 --gpus all virtual-tryon-api
```

## Customization

### Adding Custom LoRA Models

To use custom LoRA models for clothing generation:

1. Place your LoRA files in the `models/lora` directory
2. Reference them in API calls by providing the filename to the `lora_path` parameter

### Configuration

You can customize the application settings by modifying `app/config.py` or by setting environment variables.

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**: Reduce the number of samples or use a GPU with more VRAM
2. **Missing Dependencies**: Ensure all requirements are installed in both environments
3. **File Not Found Errors**: Check that all paths in the config file are correct

### Logs

Check the application logs for more details on errors:

```bash
tail -f logs/app.log
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
