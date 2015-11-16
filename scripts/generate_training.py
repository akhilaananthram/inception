#!/usr/bin/env python
import argparse
import glob
import numpy as np
import os
import shlex
import shutil
import subprocess
import tempfile

from inception.image.scene import scene

try:
  import cPickle as pkl
except ImportError:
  import pickle as pkl

if __name__ == "__main__":
  parser = argparse.ArgumentParser("Training set generator")
  parser.add_argument("--b", "--backgrounds", dest="backgrounds",
      help="Folder containing background images", required=True)
  parser.add_argument("--f", "--foregrounds", dest="foregrounds",
      help="Folder containing foreground images", required=True)
  parser.add_argument("--sd", "--scene-descriptions", dest="scene_desc",
      help="Folder containing scene descriptions for backgrounds", default="")
  parser.add_argument("--dest", help="Location to store training set",
      default=os.getcwd())

  args = parser.parse_args()

  # TODO: accept other image types
  foregrounds = np.array(glob.glob(os.path.join(args.foregrounds, "*.jpg")))
  backgrounds = np.array(glob.glob(os.path.join(args.backgrounds, "*.jpg")))

  if not os.path.isdir(args.dest):
    os.makdir(args.dest)

  curr_dir = os.getcwd()
  os.chdir(os.path.dirname(os.path.realpath(__file__)))

  # Folder for temporary scene descriptions
  o = os.path.join(args.dest, "scene_desc")
  if not os.path.isdir(o):
    os.mkdir(o)

  # Calculate the scene description for the background
  if os.path.isdir(args.scene_desc):
    scene_descriptions = np.array(glob.glob(os.path.join(args.scene_desc, "*.pkl")))
  else:
    scene_descriptions = []
    for b in backgrounds:
      bname, bext = os.path.splitext(os.path.basename(b))

      try:
        sd = scene.SceneDescription(b)
        sd_pkl = os.path.join(args.dest, "scene_desc", "{}.pkl".format(bname))
        with open(sd_pkl, "w") as f:
          pkl.dump(sd, f)
        scene_descriptions.append((sd_pkl, bname, bext))
      # TODO: figure out which exceptions could happen
      except Exception as e:
        print type(e), e
        continue

  scene_descriptions = np.array(scene_descriptions)

  for f in foregrounds:
    fname, fext = os.path.splitext(os.path.basename(f))
    o = os.path.join(args.dest, fname)

    if not os.path.isdir(o):
      os.mkdir(o)
    shutil.copy(f, os.path.join(o, "{}{}".format("iconic", fext)))

    backgrounds_sample = scene_descriptions[np.random.choice(len(scene_descriptions), min(15, len(scene_descriptions)))]
    for sd_pkl, bname, bext in backgrounds_sample:
      cmd = "python inception -s {} -e {} -o {}{} -sd {}".format(f, b, os.path.join(o, bname), bext, sd_pkl)
      print cmd
      subprocess.check_call(shlex.split(cmd))
  
  os.chdir(curr_dir)
