import argparse
import os
import shutil
import numpy as np
import glob

if __name__ == "__main__":
  parser = argparse.ArgumentParser("Copy iconic")
  parser.add_argument("--f", "--foregrounds", dest="foregrounds",
      help="Folder containing foreground images", required=True)
  parser.add_argument("--dest", help="Location to store training set",
      default=os.getcwd())
  parser.add_argument("--img-type", choices=["jpg", "png"], default="jpg",
                      help="Type of images to use")
  args = parser.parse_args()

  foregrounds = np.array(glob.glob(os.path.join(args.foregrounds, "*.{}".format(args.img_type))))
  print "Processing {} images".format(len(foregrounds))

  valid_inception = 0
  for f in foregrounds:
    fname, fext = os.path.splitext(os.path.basename(f))
    o = os.path.join(args.dest, fname)

    # already been processed by inception
    if os.path.isdir(o):
      valid_inception += 1
      shutil.copy(f, os.path.join(o, "{}{}".format("iconic", fext)))

  print "Processed {} images".format(valid_inception)
