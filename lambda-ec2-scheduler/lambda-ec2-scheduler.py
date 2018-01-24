#!/usr/bin/env python

import boto3
from datetime import datetime, timedelta
from dateutil.tz import tzutc
from croniter import croniter
from concurrent.futures import ThreadPoolExecutor

def scheduler(region):
    auto_filter = [{
            'Name': 'tag:auto',
            'Values': ['*']
        }
    ]

    try:
        print "-- Connecting to region %s" % (region)
        ec2 = boto3.resource('ec2', region)
        now = datetime.now(tzutc())
        instance_list = ec2.instances.filter(Filters=auto_filter)

        for instance in instance_list:
            try:
                auto_tag = [tag['Value'].split(';') for tag in instance.tags if tag['Key'] == 'auto'][0]
                auto_items = dict(item.split('=') for item in auto_tag if '=' in item)
                cron = dict()

                for action in ['start', 'stop']:
                    try:
                        cron[action] = (croniter(auto_items[action], now) if action in auto_items else False)
                    except Exception as e:
                        print "$s -- Invalid %s cron value for %s : %s" % (region, action, instance.id, e)
                        cron[action] = False

                if cron['start'] and instance.state['Name'] == 'stopped' and now <= cron['start'].get_next(datetime) <= now + timedelta(0, 600):
                    try:
                        print "%s -- Starting %s based on schedule: %s" % (region, instance.id, auto_items['start'])
                        instance.start()
                    except Exception as e:
                        print "%s -- Error starting %s : %s" % (region, instance.id, e)

                elif cron['stop'] and instance.state['Name'] == 'running':
                    try:
                        print "%s -- Stopping %s based on schedule: %s" % (region, instance.id, auto_items['stop'])
                        instance.stop()
                    except Exception as e:
                        print "%s -- Error stopping %s : %s" % (region, instance.id, e)

            except Exception as e:
                print "%s -- Error processing instance %s : %s" % (region, instance.id, e)
    except Exception as e:
        print "Error in region %s : %s" % (region, e)

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    awsRegions = ec2.describe_regions()['Regions']
    regions = [r['RegionName'] for r in awsRegions]

    print "-- Starting EC2 Scheduler"

    with ThreadPoolExecutor(10) as executor:
        executor.map(scheduler, regions)
