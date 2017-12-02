import os
import cv2
import torch
import config
import numpy as np
from torch.utils.data import Dataset

class_ids = {
  "Aeroplane": 0,
  "Bicycle": 1,
  "Boat": 2,
  "Bottle": 3,
  "Bus": 4,
  "Car": 5,
  "Chair": 6,
  "DiningTable": 7,
  "Motorbike": 8,
  "Sofa": 9,
  "Train": 10,
  "TvMonitor": 11
}

domain_ids = {
  "shapenet": 0,
  "imagenet": 1,
  "pascal": 1
}

class ViewpointDataset(Dataset):

  """ 
    Instance vars
    - self.data_dir => string (dir holding all ims)
    - self.ims_list => list
    - self.images => dictionary (key=filename, val=annot)
    - self.transform => transformation on image
  """

  def __init__(self, data_base_dir, data_list, data_set, transform=None):
    
    # Get list of all PNGs in data_dir
    self.data_base_dir = data_base_dir
    self.ims_list = []
    for d in data_list:
      full_d = os.path.join(data_base_dir, d, data_set)
      self.ims_list += [os.path.join(full_d, f).strip() for f in os.listdir(full_d) if (os.path.isfile(os.path.join(full_d, f)) and f.split(".")[-1] == "png")]

    # Load labels
    ims_set = set(self.ims_list)
    self.images = {}
    for d in data_list:
      data_labels_fp = os.path.join(data_base_dir, d, 'annots.txt')
      data_labels_f = open(data_labels_fp, 'r')
      lines = data_labels_f.readlines()
      data_labels_f.close()
      for l in lines:
        split = l.strip().split(",")
        im_name = "{}.png".format(split[0])
        im_fp = os.path.join(data_base_dir, d, data_set, im_name).strip()
        if im_fp in ims_set:
          self.images[im_fp] = [int(split[1]), int(split[2])]

    # Save transform
    self.transform = transform

  def __len__(self):
    return len(self.ims_list)

  def __getitem__(self, idx):
    # Fetch image
    im_fp = self.ims_list[idx].strip()
    image = cv2.imread(im_fp)

    # Fetch angle annots
    annot = self.images[im_fp]    #(azimuth, elevation)
    azimuth = annot[0]
    elevation = annot[1]
    if elevation < 0:
      elevation = 360 + elevation

    # Fetch class and domain annots
    dataset_name = im_fp.split("/")[-3].split(".")[0]
    class_id = class_ids[dataset_name.split("_")[0]]
    domain_id = domain_ids[dataset_name.split("_")[1]]

    # Return sample
    sample = {"image_fp": im_fp, "image": image, "azimuth": azimuth, "elevation": elevation, "class_id": class_id, "domain_id": domain_id}
    if self.transform:
        sample["image"] = self.transform(sample["image"])
    return sample
