import os
import json
import boto3
import uuid
import base64


def handler(event, context):
    print('[trigger lambda] payload request: {}'.format(json.dumps(event)))

    sfn = boto3.client('stepfunctions')
    res = sfn.start_execution(
        name=f"LambdaTriggered-Id-{uuid.uuid4()}",
        stateMachineArn=os.environ['STATE_MACHINE_ARN'],
        input=json.dumps({"comment": "Running more than one execution at a time",
                          "ExecutedBy": "Varun Singh", "status": "SUCCESS"})
    )

    print(res)

    # return {
    #     'statusCode': 200,
    #     'execution_response': base64.b64encode(res)
    # }
