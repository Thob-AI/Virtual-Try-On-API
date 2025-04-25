import os
from typing import Optional, List, Tuple
from PIL import Image
import io

def is_valid_image(file_path: str) -> bool:
    """Check if a file is a valid image"""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def resize_image(
    image_path: str, 
    output_path: Optional[str] = None,
    max_size: Tuple[int, int] = (1024, 1024),
    maintain_aspect: bool = True
) -> str:
    """
    Resize an image while maintaining aspect ratio
    
    Args:
        image_path: Path to the input image
        output_path: Path to save the resized image (optional)
        max_size: Maximum width and height
        maintain_aspect: Whether to maintain aspect ratio
        
    Returns:
        Path to the resized image
    """
    # Set default output path if not provided
    if output_path is None:
        filename, ext = os.path.splitext(image_path)
        output_path = f"{filename}_resized{ext}"
    
    # Open the image
    with Image.open(image_path) as img:
        # If maintaining aspect ratio
        if maintain_aspect:
            img.thumbnail(max_size, Image.LANCZOS)
        else:
            img = img.resize(max_size, Image.LANCZOS)
        
        # Save the resized image
        img.save(output_path)
    
    return output_path

def convert_image_format(
    image_path: str,
    output_format: str = "png",
    output_path: Optional[str] = None
) -> str:
    """
    Convert an image to a different format
    
    Args:
        image_path: Path to the input image
        output_format: Format to convert to (e.g., 'png', 'jpg')
        output_path: Path to save the converted image (optional)
        
    Returns:
        Path to the converted image
    """
    # Set default output path if not provided
    if output_path is None:
        filename, _ = os.path.splitext(image_path)
        output_path = f"{filename}.{output_format.lower()}"
    
    # Open the image
    with Image.open(image_path) as img:
        # Convert to RGB if needed (e.g., for PNG to JPG)
        if output_format.lower() in ['jpg', 'jpeg'] and img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save the converted image
        img.save(output_path, format=output_format.upper())
    
    return output_path
