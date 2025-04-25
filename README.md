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
- Clone the OOTD