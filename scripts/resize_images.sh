#!/bin/bash
# ./resize_images.sh INPUT_DIR OUTPUT_DIR
input_dir_offset=${#1};

for old_path in $(find "$1" -iname '*.jpg');
do
  # Set the internal field separator
  IFS="/";
  new_path=("$2""${old_path[@]:input_dir_offset}");
  directory=$(dirname "${new_path[@]}");
  mkdir -p "$directory";
  echo convert "${old_path[@]}" -resize '256x256!' "${new_path[@]}";
  convert "${old_path[@]}" -resize '256x256!' "${new_path[@]}";
done
