"""
Author: Julian Addison

Organization: Firemark Labs

folder/directory managing functions

"""

import os
import glob
import json
import boto3


def rename_files(dest_dir: str, filepaths: list, datasetname_idx: int):
    for src in filepaths:
        new_filename = src.split("/")[-datasetname_idx] + '_' + src.split('/')[-1]
        dst = os.path.join(dest_dir, *src.split("/")[1:-1], new_filename)
        print(src, dst)

        # rename() function will rename all the files
        os.rename(src, dst)
    return


def rename_dir(main_dir, dir):
    # print(dir)
    for folder in os.listdir(dir):
        # print(folder)
        src = os.path.join(dir, folder)
        dst = os.path.join(main_dir, processString(folder))

        # print(src, dst)

        # rename() function will rename all the files
        os.rename(src, dst)
    return


def processString(txt):
    specialchars = "!#$%^&*- "
    txt = txt.lower()
    txt = " ".join(txt.split())
    txt = txt.replace('(', '').replace(')', '')
    for specialchar in specialchars:
        txt = txt.replace(specialchar, '_')
        txt = txt.replace(',', ' ')
    return txt


def get_files(src_dir: str, glob_patterns: list) -> list:
    files = []
    for glob_pattern in glob_patterns:
        files += glob.glob(os.path.join(src_dir, glob_pattern))
    return files


def load_json(filepath):
    with open(filepath, 'r') as j:
        contents = json.loads(j.read())
    return contents


def write_json(filepath, json_string):
    with open(filepath, 'w') as outfile:
        json.dump(json_string, outfile)
    return


class S3BucketHandler:
    def __init__(self, download_dir, profile_name, bucket_name):
        self.download_dir = download_dir
        self.profile_name = profile_name
        self.bucket_name = bucket_name

        # Create Session
        self.session = boto3.Session(profile_name=self.profile_name)

        # Initiate S3 Resource
        self.s3 = self.session.resource('s3')

        # Select S3 Bucket
        self.bucket = self.s3.Bucket(self.bucket_name)

    def get_objects(self):
        self.object_ls = []
        for obj in self.bucket.objects.all():
            self.object_ls.append(obj.key)
        return self.object_ls

    def download_file(self, bucket_object, download_path):
        self.bucket.download_file(bucket_object, download_path)

    def download_files_in_dir(self, bucket_dir_name, file_type=None):
        self.bucket_dir_name = bucket_dir_name

        # Iterate over Objects in directory within S3 Bucket
        for obj in self.bucket.objects.filter(Prefix=self.bucket_dir_name):

            # Create download folder and filename
            self.obj_filepath, self.obj_filename = os.path.split(obj.key)

            # Download files with a pre-specified extension
            if file_type is not None and self.obj_filename.split('.')[-1] in file_type:
                # Create sub directories
                os.makedirs(self.obj_filepath, exist_ok=True)

                # Download the file in the sub directories or directory if its available.
                self.download_file(obj.key, os.path.join(self.obj_filepath, self.obj_filename))

            # Download all files
            if file_type is None:
                # Create sub directories
                os.makedirs(self.obj_filepath, exist_ok=True)

                # Download the file in the sub directories or directory if its available.
                self.download_file(obj.key, os.path.join(self.obj_filepath, self.obj_filename))