
import os
import gdown
from pathlib import Path
import boto3
from dotenv import load_dotenv
from PIL import Image


def show_image(image_path):
    """
    Opens and displays an image using PIL.

    Parameters:
        image_path (str): Path to the image file.
    """

    try:
        img = Image.open(image_path)
        img.show()
        return img
    except Exception as e:
        print("Error opening image:", e)



def connect():

  """
  connects to aws textract
  """

  load_dotenv()
  print('evironment variables loaded')

  textract_client = boto3.client('textract', region_name= os.environ['AWS_DEFAULT_REGION'])

  try:
    response = textract_client.list_adapters()
    print("✅ Textract is ready to use!")
  except Exception as e:
    print(f"Error: {e}")
  return textract_client


def get_img(url:str):
  """
  gets image in img directory and gives it's path
  as an instance of Path

  input: url of saved image in google drive
         with sharing enabled

  output: Path instance of image_path

  """

  path = Path(os.getcwd())
  img_path = path / 'img'
  img_path.mkdir(parents = True , exist_ok = True)
  print('creating img directory')

  image_path = img_path / 'testing.jpg'

  print(str(image_path))
  gdown.download(url, str(image_path), quiet=False)


  return image_path


def textractor(image_path , textract_client):
    """
    extracts text from image

    input: image_path:pathlib.Path 
           textract_client -> it is the output of connect() function
           
    output: list of extracted lines 


    """
    extracted_lines = []

    with open(str(image_path), 'rb') as image_file:
        response = textract_client.detect_document_text(
            Document={'Bytes': image_file.read()}
        )

    # Extract text
    for block in response['Blocks']:
        if block['BlockType'] == 'LINE':
            extracted_lines.append(block['Text'])
            print(block['Text'])
    return extracted_lines
