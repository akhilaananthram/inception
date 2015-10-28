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
      help="Folder containing background images")
  parser.add_argument("--f", "--foregrounds", dest="foregrounds",
      help="Folder containing foreground images")
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
  tempdir = tempfile.mkdtemp()

  # Calculate the scene description for the background
  for b in backgrounds:
    bname, bext = os.path.splitext(os.path.basename(b))

    sd = scene.SceneDescription(b)
    sd_pkl = os.path.join(tempdir, "{}.pkl".format(bname))
    with open(sd_pkl, "w") as f:
      pkl.dump(sd, f)

  for f in foregrounds:
    fname, fext = os.path.splitext(os.path.basename(f))
    o = os.path.join(args.dest, fname)

    if not os.path.isdir(o):
      os.mkdir(o)
    shutil.copy(f, os.path.join(o, "{}{}".format("iconic", fext)))

    backgrounds_sample = backgrounds[np.random.choice(len(backgrounds), min(15, len(backgrounds)))]
    for b in backgrounds_sample:
      bname, bext = os.path.splitext(os.path.basename(b))
      sd_pkl = os.path.join(tempdir, "{}.pkl".format(bname))

      cmd = "python inception -s {} -e {} -o {}{} -sd {}".format(f, b, os.path.join(o, bname), bext, sd_pkl)
      print cmd
      subprocess.check_call(shlex.split(cmd))
  
  os.chdir(curr_dir)
