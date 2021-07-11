import json


def handler(event, context):
    print('[second lambda] payload request: {}'.format(json.dumps(event)))
    return {
        'statusCode': 200,
        'Seconds': 10,
        'waitSeconds': 10,
        'status': event['status'],
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Hello, CDK! You have hit {}\n'.format(event['ExecutedBy']),
        'ExecutedBy': event['ExecutedBy']

    }
