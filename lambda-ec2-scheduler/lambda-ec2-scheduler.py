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
        print(f'-- Connecting to region {region}')
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
                    except Exception as err:
                        print(f'{region} -- Invalid {action} cron value for {instance.id} : {err}')
                        cron[action] = False

                if cron['start'] and instance.state['Name'] == 'stopped' and now <= cron['start'].get_next(datetime) <= now + timedelta(0, 600):
                    try:
                        print(f'{region} -- Starting {instance.id} based on schedule: {auto_items["start"]}')
                        instance.start()
                    except Exception as err:
                        print(f'{region} -- Error starting {instance.id} : {err}')

                elif cron['stop'] and instance.state['Name'] == 'running'  and now - timedelta(0, 600) <= cron['stop'].get_prev(datetime) <= now:
                    try:
                        print(f'{region} -- Stopping {instance.id} based on schedule: {auto_items["stop"]}')
                        instance.stop()
                    except Exception as err:
                        print(f'{region} -- Error stopping {instance.id} : {err}')

            except Exception as err:
                print(f'{region} -- Error processing instance {instance.id} : {err}')
    except Exception as err:
        print(f'Error in region {region} : {err}')

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    awsRegions = ec2.describe_regions()['Regions']
    regions = [r['RegionName'] for r in awsRegions]

    print('-- Starting EC2 Scheduler')

    with ThreadPoolExecutor(10) as executor:
        executor.map(scheduler, regions)