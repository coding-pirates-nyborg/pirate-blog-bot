from wand.image import Image
import tempfile
import os

def process_image(image_data: bytes, target_format: str = 'webp') -> tuple[bytes, str]:
    """
    Process an image using ImageMagick via Wand.
    Returns processed image data and filename.
    """
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(image_data)
        temp_file.flush()
        
        with Image(filename=temp_file.name) as img:
            # Optimize the image
            img.compression_quality = 85
            
            # Convert to target format
            img.format = target_format
            
            # Save to new temp file
            output_path = f"{temp_file.name}.{target_format}"
            img.save(filename=output_path)
    
    # Read processed image
    with open(output_path, 'rb') as f:
        processed_data = f.read()
    
    # Cleanup
    os.unlink(temp_file.name)
    os.unlink(output_path)
    
    return processed_data, f"{target_format}" 