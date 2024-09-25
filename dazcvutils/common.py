import io
import json
import logging
import requests
import base64
from PIL import Image
from io import BytesIO
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QByteArray

# Create a logger
logger = logging.getLogger("core")
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)

# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Example usage
logger.info("Logging system initialized.")


def cleanify(argmap, kvarglist):

    args={}

    for key in argmap:
        if key in kvarglist:
            submap=argmap[key]
            submap_ext={}
            for k2 in submap:
                print (f"X+++++ {k2} +++++")
                parts=k2.split("=")
                k=v=None
                if len(parts) == 1:
                    k=parts[0].strip()
                    v=''
                else:
                    k=parts[0].strip()
                    v=parts[1].strip()
                submap_ext[k]=v
            args[key]=submap_ext
        else:
            args[key]=argmap[key] 
    return args

def get_daz_product_data(sku, full_url):
    headers = {'Content-Type': 'application/json'}        
    content = None
    
    try:
        response = requests.get(full_url, headers=headers, allow_redirects=True)
        content = json.loads(response.text)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to process request: {str(e)}")
        
    return content



def base64_to_image(base64_string):
  """Converts a base64 string to an image.

  Args:
    base64_string: The base64 encoded string representing the image.

  Returns:
    A PIL Image object representing the decoded image.
  """

  # Remove the 'data:image/png;base64,' prefix if present
  if base64_string.startswith('data:image/png;base64,'):
    base64_string = base64_string[len('data:image/png;base64,'):]
  elif base64_string.startswith('data:image/jpeg;base64,'):
    base64_string = base64_string[len('data:image/jpeg;base64,'):]

  # Decode the base64 string
  image_bytes = base64.b64decode(base64_string)

  # Create a PIL Image object from the decoded bytes
  image = Image.open(io.BytesIO(image_bytes))

  return image

def image_to_qpixmap(image):
  """Converts a PIL Image object to a QPixmap.

  Args:
    image: The PIL Image object to convert.

  Returns:
    A QPixmap object representing the image.
  """

  # Convert the PIL Image to a byte stream
  buffer = BytesIO()
  image.save(buffer, format="PNG")  # You can change the format if needed
  buffer.seek(0)
  byte_array = buffer.getvalue()

  # Create a QByteArray from the byte stream
  q_byte_array = QByteArray(byte_array)

  # Create a QPixmap from the QByteArray
  qpixmap = QPixmap()
  qpixmap.loadFromData(q_byte_array)

  return qpixmap

