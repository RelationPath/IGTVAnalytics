import argparse
import io
import re

from google.cloud import storage
from google.cloud import vision
from google.protobuf import json_format

inputUri = 'https://storage.googleapis.com/igtv-input-data/Sample%20Data/Screenshot_20180713-153744.png'

def detect_text_uri(uri):
   """Collects input when user calls on program to detect text from teh command line and saves the uri given after the call as the variable to be called on in the program"""

   client = vision.ImageAnnotatorClient()
   image = types.Image()
   image.source.image_uri = uri
   """defines the uri to be called on as what the user defined it to be in the command call"""

   response = client.text_detection(image=image)
   texts = response.text_annotations
   print('Texts:')

   for text in texts:
      print('\n"{}"'.format(text.description))

   vertices = (['({},{})'.format(vertex.x, vertex.y)
         for vertex in text.bounding_poly.vertices])

   print('bounds: {}'.format(','.join(vertices)))

print(detect_text_uri(inputUri))

def run_uri(args):
    if args.command == 'text-uri':
        detect_text_uri(args.uri)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest='command')

    text_file_parser = subparsers.add_parser(
        'text-uri', help=detect_text_uri.__doc__)
    text_file_parser.add_argument('uri')
