#
# Licensed under GNU General Public License v3.0 (see LICENSE file)
#
# Given the ID of an Amazon public AMI in one region, figure out what the
# equivalent AMI IDs are for that same AMI in all other regions known.
# If that AMI isn't defined in a region, it prints the region's name, but
# comments it out.
#

from __future__ import print_function
import boto3

# Get a starting point by finding a value in the table on this page or similar page.
# https://aws.amazon.com/amazon-linux-ami/
#
# Alternatively, you can run something like:
# aws ec2 describe-images --owners amazon --filter "Name=description,Values=Amazon Linux AMI 2017*" |
#   jq -c '.Images[] | {ImageId, Name, Description}'
#
# It will list images in the current region based on the filter expression. From there, you can
# figure out which image suits your needs. Stick the region and AMI identifier below.

# This is "ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-20190722.1"
BASEAMI="ami-07d0cf3af28718ef8"
BASEREGION="us-east-1"
MAPNAME="Ubuntu18AMIForRegion"
KEYNAME="x86"

# AMI filter
image_filter = [{'Name':'image-id', 'Values':[BASEAMI]}]

# List all regions
client = boto3.client('ec2', region_name=BASEREGION)
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

ec2 = boto3.resource('ec2', region_name=BASEREGION)

# Figure out what the AWS Name is for this image.
image_names = list(ec2.images.filter(Filters=image_filter).all())
if( len(image_names) != 1 ):
    print( "ERROR: ", len(image_names), "matched", BASEAMI)
    exit( 1 )

print( "# image name is:\"" + image_names[0].name + "\"" )
target_image = image_names[0].name
# name-based filter
name_filter = [{'Name':'name', 'Values': [target_image] }]

# Print the first lines of YAML
print( "  {}:".format(MAPNAME) )
print( "    {}:".format(BASEREGION)  )
print( "      {}: \"{}\"".format(KEYNAME, BASEAMI) )

# For every region, look up the AMI ID for that region by looking for
# the image with the same name.
for r in regions:
    ec2 = boto3.resource('ec2', region_name=r)
    image_names = list(ec2.images.filter(Filters=name_filter).all())
    if( len(image_names) != 1 ):
        print( "#  {}: undefined".format(r) )
    elif( r != BASEREGION ):
        print( "    {}:".format(r) )
        print( "      {}: \"{}\"".format(KEYNAME, image_names[0].id ) )
