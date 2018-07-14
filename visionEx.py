import io
import os
import google.cloud.vision

vision_client = google.cloud.vision.ImageAnnotatorClient()
file_name = 'igtv-grid-2_1530180266779.jpg'

with io.open(file_name,'rb') as image_file:

   content = image_file.read()
   
image = google.cloud.vision.types.Image(content=content)
response = vision_client.label_detection(image=image)

print('Labels:')
for label in response.label_annotations:
   print(label.description)
