import redis
import argparse
import io
import re

from google.cloud import storage
from google.cloud import vision
from google.protobuf import json_format

r = redis.StrictRedis(
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
   print('Indexed!')

   account = 'was not found'
   date = 'was not found'
   length = 'was not found'
   title = 'was not found'
   views = 'was not found'
   comments = 'was not found'

   progressDate = ''
   date = ''
   title = '' 
   lastStore = ''
   onTitle = True
   onAccount = True

   for text in texts:
      textDescription = u'{}'.format(text.description)
      #print(textDescription.encode('utf-8'))

      vertices = (['({},{})'.format(vertex.x, vertex.y)
            for vertex in text.bounding_poly.vertices])

      if vertex.y < 155:
         title = title + " " +  textDescription.encode('utf-8')
         progressTitle = textDescription.encode('utf-8')
      elif vertex.x > 44 and vertex.y in range(155,250):
         if onAccount:
            account = textDescription.encode('utf-8')
            onAccount = False
         else: 
            date = date + " " +  textDescription.encode('utf-8')
      #elif vertex.x in range(300,1000) and vertex.y in range(121,185):
         #date = progressDate + " " +  textDescription.encode('utf-8')
         #progressDate = textDescription.encode('utf-8')
      elif vertex.x in range(920,935) and vertex.y in range(1725,1740):
         length = textDescription.encode('utf-8')
      elif textDescription.encode('utf-8') == 'views':
         views = lastStore
      elif textDescription.encode('utf-8') == 'comments':
         comments = lastStore

      lastStore = textDescription.encode('utf-8')

   print(account + '/' + date + '/' + length + '/' + title + '/' + views + '/' + comments)

   r.lpush(account + '-dates', "/" + title + "/, was released: " + date + "           ")
   r.lpush(account + '-lengths', "/" + title + "/, length: " + length + "          ")
   r.lpush(account + '-titles', title + "         ")
   r.lpush(account + '-views',  "/" + title + "/, view count: " + views + "           ")
   r.lpush(account + '-comments', "/" + title + "/, comment count: " + comments + "           ")

def redis_scan(leadData):
   value = r.lrange(leadData, 0, -1)
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
