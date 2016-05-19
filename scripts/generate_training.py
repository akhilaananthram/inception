#!/usr/bin/env python
import argparse
import cv2
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
  parser.add_argument("--num-in-situ", dest="in_situ", default=15,
      help="Number of in situ images to make for each iconic image")
  parser.add_argument("--job-id", dest="job_id", type=int, default=0,
      help="Job id if parallelizing the program on --num-jobs machines between [0, num_jobs - 1]")
  parser.add_argument("--num-jobs", dest="num_jobs", type=int, default=1,
      help="Number of machines you are parallelizing on")
  parser.add_argument("--img-type", choices=["jpg", "png"], default="jpg",
                      help="Type of images to use")

  args = parser.parse_args()

  if args.job_id < 0 or args.job_id >= args.num_jobs:
    raise Exception("Job id must be in the range [0, num_jobs - 1]")

  # TODO: accept other image types
  # sample from forgrounds to parallelize
  foregrounds = np.array(glob.glob(os.path.join(args.foregrounds, "*.{}".format(args.img_type))))[args.job_id::args.num_jobs]

  if not os.path.isdir(args.dest):
    os.makdir(args.dest)

  curr_dir = os.getcwd()
  os.chdir(os.path.dirname(os.path.realpath(__file__)))

  # Folder for temporary scene descriptions
  if os.path.isdir(args.scene_desc):
    o = args.scene_desc
  else:
    o = os.path.join(args.dest, "scene_desc")
    if not os.path.isdir(o):
      os.mkdir(o)

  # Get the pre-computed scene descriptions, if any
  scene_descriptions = glob.glob(os.path.join(o, "*.pkl"))

  # Calculate the scene description for the remaining backgrounds
  backgrounds = glob.glob(os.path.join(args.backgrounds, "*.{}".format(args.img_type)))
  for b in backgrounds:
    bname, _  = os.path.splitext(os.path.basename(b))

    sd_pkl = os.path.join(o, "{}.pkl".format(bname))
    if not os.path.isfile(sd_pkl):
      try:
        sd = scene.SceneDescription(b)
        with open(sd_pkl, "w") as f:
          pkl.dump(sd, f)
        scene_descriptions.append(sd_pkl)
      except Exception as e:
        print type(e), e
        continue
  scene_descriptions = np.array(scene_descriptions)

  mid_shapes = {}
  for f in foregrounds:
    fname, fext = os.path.splitext(os.path.basename(f))
    o = os.path.join(args.dest, fname)

    if not os.path.isdir(o):
      os.mkdir(o)

    in_situ = [f for f in glob.glob(os.path.join(o, "*.{}".format(fext))) if not f.endswith("iconic.{}".format(fext))]
    if len(in_situ) >= args.in_situ:
      continue
    shutil.copy(f, os.path.join(o, "{}{}".format("iconic", fext)))

    f_height, f_width = (cv2.imread(f)).shape[:2]
    f_height, f_width = (f_height / 2, f_width / 2)

    # TODO: ignore any backgrounds that have already been done
    sample = np.random.choice(len(scene_descriptions), min(args.in_situ - len(in_situ), len(scene_descriptions)))
    backgrounds_sample = scene_descriptions[sample]
    for sd_pkl in backgrounds_sample:
      bname, _  = os.path.splitext(os.path.basename(sd_pkl))
      e = "{}.{}".format(os.path.join(args.backgrounds, bname), fext)
      out_file = "{}.{}".format(os.path.join(o, bname), fext)

      # get bounding box
      if e not in shapes:
        e_height, e_width = (cv2.imread(e)).shape[:2]
        e_height, e_width = (e_height / 2, e_width / 2)
        mid_shapes[e] = (e_height, e_width)
      else:
        e_height, e_width = mid_shapes[e]
      up_l_x = e_width - f_width
      up_l_y = e_height - f_height
      lo_r_x = e_width + f_width
      lo_r_y = e_height + f_height

      bounding_box = "{} {} {} {}".format(up_l_x, up_l_y, lo_r_x, lo_r_y)
      cmd = "python inception -s {} -e {} -o {} -sd {} -b {}".format(f, e, out_file, sd_pkl, bounding_box)
      print cmd
      try:
        subprocess.check_call(shlex.split(cmd))
      except Exception as e:
        print type(e), e
        continue
  
  os.chdir(curr_dir)
