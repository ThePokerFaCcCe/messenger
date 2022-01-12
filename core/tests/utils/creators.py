from PIL import Image
import tempfile


def create_image(size=(10, 10)):
    """Create temp image file"""
    f = tempfile.NamedTemporaryFile(suffix='.jpg')
    img = Image.new('RGB', size)
    img.save(f, format='JPEG')
    f.seek(0)  # Set pointer at first of file
    return f
