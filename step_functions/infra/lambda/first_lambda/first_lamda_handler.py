import json


def handler(event, context):
    print('[first lambda] payload request: {}'.format(json.dumps(event)))
    return {
        'statusCode': 200,
        'status': event['status'],
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Hello, CDK! You have hit {}\n'.format(event['ExecutedBy']),
        'ExecutedBy': event['ExecutedBy']
    }
