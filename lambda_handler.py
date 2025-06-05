import boto3
import json

rds = boto3.client('rds')

def lambda_handler(event, context):

    print(f"Received event: {json.dumps(event)}")
    
    action = None
    
    # Check if event has custom detail with action
    if 'detail' in event and 'action' in event['detail']:
        action = event['detail']['action'].lower()
    
    print(f"Determined action: {action}")
    
    if action == 'stop':
        stop_db_instances()
    elif action == 'start':
        start_db_instances()
    else:
        print(f"Unknown action: {action}")
        return {
            'statusCode': 400,
            'body': json.dumps(f'Unknown action: {action}')
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Successfully processed {action} action')
    }

def stop_db_instances():
    """Stop RDS instances with autostop=yes tag"""
    print("Starting DB instance shutdown process...")
    
    try:
        dbs = rds.describe_db_instances()
        stopped_instances = []
        
        for db in dbs['DBInstances']:
            # Check if DB instance is available (running)
            if db['DBInstanceStatus'] == 'available':
                try:
                    get_tags = rds.list_tags_for_resource(ResourceName=db['DBInstanceArn'])['TagList']
                    
                    # Check for autostop tag
                    for tag in get_tags:
                        if tag['Key'] == 'autostop' and tag['Value'].lower() == 'yes':
                            # rds.stop_db_instance(DBInstanceIdentifier=db['DBInstanceIdentifier'])
                            stopped_instances.append(db['DBInstanceIdentifier'])
                            print(f"Stopping instance: {db['DBInstanceIdentifier']}")
                            break

                    print(f"Total instances stopped: {len(stopped_instances)}")
                
                except Exception as e:
                    print(f"Cannot stop instance {db['DBInstanceIdentifier']}: {str(e)}")

            else:
                print(f"No instances available to stop")
                
            
        
    except Exception as e:
        print(f"Error in stop_db_instances: {str(e)}")
        raise

def start_db_instances():
    """Start RDS instances with autostart=yes tag"""
    print("Starting DB instance startup process...")
    
    try:
        dbs = rds.describe_db_instances()
        started_instances = []
        
        for db in dbs['DBInstances']:
            # Check if DB instance is stopped
            if db['DBInstanceStatus'] == 'stopped':
                try:
                    get_tags = rds.list_tags_for_resource(ResourceName=db['DBInstanceArn'])['TagList']
                    
                    # Check for autostart tag
                    for tag in get_tags:
                        if tag['Key'] == 'autostart' and tag['Value'].lower() == 'yes':
                            # rds.start_db_instance(DBInstanceIdentifier=db['DBInstanceIdentifier'])
                            started_instances.append(db['DBInstanceIdentifier'])
                            print(f"Starting instance: {db['DBInstanceIdentifier']}")
                            break

                    print(f"Total instances started: {len(started_instances)}")
            
                except Exception as e:
                    print(f"Cannot start instance {db['DBInstanceIdentifier']}: {str(e)}")
                    
            else:
                 print(f"No instances avaialble to stop")

                
        
    except Exception as e:
        print(f"Error in start_db_instances: {str(e)}")
        raise
