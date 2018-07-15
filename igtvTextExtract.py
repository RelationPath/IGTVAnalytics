import argparse 
from enum import Enum
import io

from google.cloud import vision
from google.cloud.vision import types
from PIL imprt Image, ImageDraw

class FeatureType(Enum):
   PAGE = 1
   BLOCK = 2
   PARA = 3
   WORD = 4
   SYMBOL = 5


def draw_boxes(image, bounds, color):
   """Draw a border around tehe image using what is given in the vector list assinged above"""
   draw = ImageDraw.Draw(image)

   for bound in bounds:
      draw.polygon
   """Unfinished!"""
