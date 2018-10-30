#By: Brayton Kerekffy for Relation Path
import argparse
import datetime
import pprint
import redis
import argparse
import io
import re
import os
import csv
import datetime
import sys
import time

from google.cloud import storage
from google.cloud import vision
from google.protobuf import json_format
from google.cloud import pubsub_v1

# [END storage_upload_file]
now = datetime.datetime.now()

inputBucketSet = "igtv-input-data"
outputBucketSet = "igtv-analytics"

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
      elif vertex.x in range(920,935) and vertex.y in range(1725,1740):
         length = textDescription.encode('utf-8')
      elif textDescription.encode('utf-8') == 'views':
         views = lastStore
      elif textDescription.encode('utf-8') == 'comments':
         comments = lastStore

      lastStore = textDescription.encode('utf-8')

   print(account + '/' + date + '/' + length + '/' + title + '/' + views + '/' + comments)

   r.lpush(account + '-dates', "/" + title + "/, was released: " + date)
   r.lpush(account + '-lengths', "/" + title + "/, length: " + length)
   r.lpush(account + '-titles', title)
   r.lpush(account + '-views',  "/" + title + "/, view count: " + views)
   r.lpush(account + '-comments', "/" + title + "/, comment count: " + comments)

def redis_scan(leadData, bucket_name, blob_name):
   csvFileName = leadData + '-' + '%d' % now.month + ',' + '%d' % now.day + ',' + '%d' % now.year  + '.csv'
   print(csvFileName)
   os.system('redis-cli --csv lrange ' + leadData + ' 0 -1 >' + csvFileName)
   storage_client = storage.Client()
   bucket = storage_client.get_bucket(bucket_name)
   blob = bucket.blob(blob_name)

   blob.upload_from_filename(csvFileName)

   print('File {} uploaded to {}.'.format(
        csvFileName,
        blob_name))
# [END storage_upload_file]

def receive_messages(project_id, subscription_name):
    subscriber = pubsub_v1.SubscriberClient()
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_name}`
    subscription_path = subscriber.subscription_path(
        project_id, subscription_name)


    """Receives messages from a pull subscription."""

    # TODO project_id = "Your Google Cloud Project ID"
    # TODO subscription_name = "Your Pub/Sub subscription name"

    subscriber = pubsub_v1.SubscriberClient()
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_name}`
    subscription_path = subscriber.subscription_path(
        project_id, subscription_name)

    def callback(message):
        messageData = '{}'.format(message.data)
	print('{}'.format(message.data))
        print('Listening for messages on {}'.format(subscription_path))
        csvFileName = messageData + '-' + '%d' % now.month + ',' + '%d' % now.day + ',' + '%d' % now.year  + '.csv'
        redis_scan(messageData, outputBucketSet, csvFileName)
        message.ack()

    subscriber.subscribe(subscription_path, callback=callback)
    # The subscriber is non-blocking. We must keep the main thread from
    # exiting to allow it to process messages asynchronously in the background.
   # while True:
       # time.sleep(60)
    # [END pubsub_subscriber_async_pull]
    # [END pubsub_quickstart_subscriber]

def rclone_transfer():
    os.system("rclone copy gDriveIGTV:GooglePhotos gCloudIGTV:igtv-input-data")
    os.system("rclone delete gDriveIGTV:GooglePhotos")
    print('transfered!')

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()

    print('Blob {} deleted.'.format(blob_name))

def make_blob_public(bucket_name, blob_name):
    """Makes a blob publicly accessible."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.make_public()
    blobURI = blob.public_url
    detect_text_uri(blobURI)
    print('Blob {} is publicly accessible at {}'.format(
        blob.name, blob.public_url))
    delete_blob(bucket_name, blob_name)

def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blobs = bucket.list_blobs()

    for blob in blobs:
        make_blob_public(inputBucketSet, blob.name)
	receive_messages('igtv-analytics-system','csvRequest')
    rclone_transfer()
    list_blobs(inputBucketSet)

list_blobs(inputBucketSet)
