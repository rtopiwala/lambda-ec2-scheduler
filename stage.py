#!/usr/bin/env python

# Automate zip file and S3 upload.
# Create archive only:
# $ python stage.py
# Create archive and upload to S3:
# $ python stage.py -b bucket-name/key-name

import shutil
import boto3
import sys
import argparse


def zip_file(archive_name):
    return shutil.make_archive(archive_name,'zip',archive_name)


def upload_file(arg, archive_name):
    file = (zip_file(archive_name)).split('/')[-1]
    bucket = arg[0]

    if arg.__len__() == 2:
        key = arg[1]
        keyFile = ''.join([key,'/',file])
    else:
        keyFile = file

    s3 = boto3.resource('s3')
    s3.Bucket(bucket).upload_file(file, keyFile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bucket",
        help="S3 bucket name including any key name. e.g. bucket-name/key-name")
    arg = parser.parse_args()

    if arg.bucket:
        argList = arg.bucket.strip('/').split('/', 1)

        upload_file(argList,'lambda-ec2-scheduler')
        print "-- Lambda function deployed to %s" % (arg.bucket)
    else:
        print "-- Created %s " % zip_file('lambda-ec2-scheduler')
