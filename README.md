# DB Auto Stop Lambda

This project contains an AWS Lambda function designed to automatically stop RDS instances that have been tagged with a specific tag. This solution helps optimize costs by ensuring that non-production RDS instances are not running unnecessarily during off-hours or non-business periods.

## Why Stop RDS Instances Automatically?

### Cost Optimization Benefits

Stopping RDS instances temporarily is one of the most effective ways to reduce AWS costs for non-production workloads. When a DB instance is stopped, you're not charged for DB instance hours, which can result in significant savings. However, you will still be charged for:
- Provisioned storage (including Provisioned IOPS)
- Backup storage (manual snapshots and automated backups)

### Common Use Cases

This automated solution is particularly valuable for:

- **Development Environments**: Development databases that only need to run during business hours can be automatically stopped outside working hours
- **Testing Environments**: Temporary DB instances used for testing backup procedures, migrations, or application upgrades can be stopped when not actively in use
- **Training Environments**: Training databases can be started during training sessions and automatically shut down afterward
- **Non-Production Workloads**: Any database that doesn't require 24/7 availability

### Automatic Restart Protection

AWS automatically restarts stopped DB instances after 7 consecutive days to ensure they don't fall behind required maintenance updates. This Lambda function can be scheduled to run weekly (or more frequently) to maintain cost savings while respecting this limitation.

## How It Works

The Lambda function uses EventBridge scheduling to:
1. Run on a predetermined schedule (e.g., weekly on Sundays)
2. Scan for RDS instances tagged with the `autostop: yes` tag
3. Stop qualifying instances that are currently running
4. Provide logging for audit and troubleshooting purposes

## Features

- Automatically stops RDS instances based on a specific tag (`autostop: yes`)
- Scheduled execution using Amazon EventBridge (configurable frequency)
- Cost-effective approach to managing non-production RDS instances
- Respects AWS's 7-day automatic restart limitation
- CloudWatch logging for monitoring and troubleshooting

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured with access to Lambda, RDS, and EventBridge services
- Basic knowledge of AWS Lambda, RDS, and EventBridge
- Understanding of your organization's database usage patterns

## Supported Database Engines

This solution works with all supported RDS database engines that support the stop/start functionality:
- Amazon RDS for MySQL
- Amazon RDS for PostgreSQL
- Amazon RDS for MariaDB
- Amazon RDS for Oracle
- Amazon RDS for SQL Server
- Amazon RDS for Db2

**Note**: RDS for SQL Server in Multi-AZ deployments cannot be stopped.

## Setup Instructions

### 1. Deploy the Lambda Function

1. **Create a Lambda Function:**
   - Go to the AWS Lambda console
   - Click on "Create function"
   - Choose "Author from scratch"
   - Enter a function name, e.g., `DBAutoStopLambda`
   - Choose Python 3.x as the runtime
   - Create or use an existing execution role with the following permissions:
     - `rds:DescribeDBInstances`
     - `rds:StopDBInstance`
     - `rds:ListTagsForResource`
     - `logs:CreateLogGroup`
     - `logs:CreateLogStream`
     - `logs:PutLogEvents`

2. **Upload the Code:**
   - Write the Lambda function code to identify and stop RDS instances with the appropriate tag
   - Configure appropriate timeout (recommended: 5-10 minutes for larger environments)
   - Set up environment variables for configuration if needed

### 2. Add the AutoStop Tag to RDS Instances

**Important**: Only tag non-production databases that can safely be stopped without impacting critical operations.

1. **Navigate to RDS Console:**
   - Go to the AWS RDS console
   - Select the RDS instances you want managed by the Lambda function

2. **Add the Tag:**
   - Click on "Tags" in the instance details
   - Add a new tag with key `autostop` and value `yes`
   - **Verify** that these instances can be safely stopped during your scheduled maintenance windows

### 3. Schedule the Lambda Function with EventBridge

1. **Create an EventBridge Rule:**
   - Go to the Amazon EventBridge console
   - Click on "Create rule"
   - Enter a descriptive name (e.g., `weekly-db-autostop-rule`)

2. **Define the Schedule:**
   - Choose "Schedule" as the rule type
   - Recommended schedule options:
     - Weekly: `cron(0 2 ? * SUN *)` (every Sunday at 2 AM UTC)
     - Weekdays only: `cron(0 19 ? * MON-FRI *)` (Monday-Friday at 7 PM UTC)
     - Custom schedule based on your organization's needs

3. **Add Target:**
   - Choose "Lambda function" as the target
   - Select your `DBAutoStopLambda` function
   - Configure input transformer if needed for different environments

4. **Configure Permissions:**
   - Ensure EventBridge has permission to invoke the Lambda function
   - Add resource-based policy to Lambda if needed

## Important Considerations

### Before Implementation

- **Test thoroughly** in a development environment
- **Coordinate with your team** to ensure stopping instances won't disrupt ongoing work
- **Document your tagging strategy** and communicate it to all relevant teams
- **Consider timezone differences** when scheduling the EventBridge rule

### Limitations to Consider

Be aware of the following RDS stop limitations:
- Cannot stop DB instances that have read replicas or are read replicas
- Cannot modify stopped DB instances
- Multi-AZ SQL Server instances cannot be stopped
- Starting a stopped instance requires recovery time that can range from minutes to hours

## Testing

1. **Manual Testing:**
   - Add the `autostop: yes` tag to a test RDS instance
   - Manually invoke the Lambda function from the AWS console
   - Verify the instance stops successfully
   - Check CloudWatch logs for proper execution

2. **Schedule Testing:**
   - Create a test EventBridge rule with a short interval
   - Monitor execution over several cycles
   - Verify consistent behavior and logging

3. **Recovery Testing:**
   - Test manually starting stopped instances
   - Measure startup times for capacity planning
   - Verify application reconnection after restart

## Monitoring and Logging

- Monitor Lambda execution through CloudWatch Logs
- Set up CloudWatch alarms for Lambda failures
- Track cost savings through AWS Cost Explorer
- Consider setting up SNS notifications for execution status

## Cost Impact

Based on typical usage patterns, this solution can reduce RDS costs by:
- **50-70%** for development environments (running only during business hours)
- **85%** for weekend-only testing environments
- **Variable savings** depending on your specific usage patterns
