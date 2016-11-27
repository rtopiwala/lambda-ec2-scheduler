# lambda-ec2-scheduler
## Schedule your EC2 instances with the flexibility of Cron

lambda-ec2-scheduler allows you to run a lean, multi-threaded EC2 scheduling service powered by AWS Lambda and CloudWatch Events. Scheduling for each EC2 instance is performed based on its assigned Cron values, giving you the upmost flexibility for configuring your start & stop times.

Once deployed, the scheduler requires virtually zero maintenance and annual costs should remain less than $10 for running in enterprise-size environments.

## Architecture
![lambda-ec2-scheduler](https://cloud.githubusercontent.com/assets/2275245/19966847/8dfc33a0-a208-11e6-9556-264c7a015704.JPG)

## Installation

CloudFormation Template
* cloudformation/lambda-ec2-scheduler-cf.yaml

## Usage

Once the service is deployed through CloudFormation the Lambda function will automatically run on a user-defined schedule (every 5 mins recommended) and scan all EC2 instances for a tag named **auto**. If an instance has the **auto** tag, Lambda will read the tag's start/stop values and perform the action if the Cron value is within the valid timeframe.

#### Valid timeframes
The scheduler is configured to perform start/stop actions within valid timeframes to provide a safety net in case of unforeseeable events like AWS service disruption or tag misconfiguration.

The default timeframe to start instances is configured as *current time + 10 mins*. This means the scheduler may start the instance up to 10 mins earlier than its scheduled Cron time.

The default timeframe to stop instances is set to *launch time < current time - 50 mins*. This means the scheduler will stop the instance at the scheduled time as long as the launch time was not within the past 50 mins.

These values can be updated in the Lambda file to fit your requirements.

#### Add/remove instances to scheduler
The only action needed to add or remove an EC2 instance to the scheduling service is to update its **auto** tag.

#### Configuring the tag
For each instance that is to be scheduled, the format of its **auto** tag value should be:

`start=0 8 * * 1-5;stop=0 17 * * 1-5`

*This example indicates the instance should start at 8:00 and stop at 17:00 every day of the week, Monday through Friday.*

## FAQ
**Q: Does there need to be a value for both start and stop? What if I want to only start (or stop) my instance?**

The scheduler service supports single actions. Simply enter a value for the **auto** tag that describes the single action and leave the other action out. e.g. `stop=* * * * *`

**Q: Does the scheduler scan EC2 instances in all regions?**

Yes, a single deployment of the service will scan all EC2 instances in all regions under one AWS account. Each AWS account will need its own lambda-ec2-scheduler deployment.

**Q: Does the scheduler produce logs? Where can I see them?**

Yes, the Lambda function automatically logs its events to CloudWatch Logs with details of each scheduled run.

**Q: The scheduler returns and error when reading the tag's Cron value. How can I troubleshoot this?**

The Cron value may need to reformatted before the Lambda function can read it. Try validating the Cron value at http://cron.schlitt.info/

**Q: What can I do to increase the performance of the scheduler?**

The scheduler processes each region asynchronously. increase the memory size of the Lambda function and more CPU threads will be allocated to increase performance. Note, the increased size results in faster processing so the costs will remain roughly the same as the smaller function and the function will finish sooner.

## License
[MIT License](../master/LICENSE)
© Rohan Topiwala
