import redis
import argparse
import io
import re

from google.cloud import storage
from google.cloud import vision
from google.protobuf import json_format

r = redis.Redis(
   host='127.0.0.1',
   port=6379,
   password='')

def detect_text_uri(uri):
   """Collects input when user calls on program to detect text from the command line and saves the uri given after the call as the variable to be called on in the program"""

   client = vision.ImageAnnotatorClient()
   image = vision.types.Image()
   image.source.image_uri = uri

   """defines the uri to be called on as what the user defined it to be in the command call"""

   response = client.text_detection(image=image)
   texts = response.text_annotations
   print('Texts:')

   for text in texts:
      textDescription = u'{}'.format(text.description)
      print(textDescription.encode('utf-8'))

      vertices = (['({},{})'.format(vertex.x, vertex.y)
         for vertex in text.bounding_poly.vertices])

      if vertex.x in range(130,140) and vertex.y in range(175,185):
         title = textDescription.encode('utf-8')
         print('title is:' and title)
      elif vertex.x in range(920,935) and vertex.y in range(1725,1740):
         r.set(title +  '-length', textDescription.encode('utf-8'))
         print('indexed vLength')
      else:
         print(vertex.x)
         print(vertex.y)

   print('bounds: {}'.format(','.join(vertices)))

def redis_scan(leadData):
   value = r.get(leadData)
   print('scanned!')
   print(value)

def run_local(args):
    if args.command == 'redis-scan':
        redis_scan(args.leadData)

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

    redis_scan_parser = subparsers.add_parser(
        'redis-scan', help=redis_scan.__doc__)
    redis_scan_parser.add_argument('leadData')

    args = parser.parse_args()

    if 'uri' in args.command:
        run_uri(args)
    else:
        run_local(args)
