#!/usr/bin/env python3
import os
from aws_cdk import core as cdk
from aws_cdk import core

from step_functions.step_functions_stack import StepFunctionsStack


app = core.App()
StepFunctionsStack(app, "StepFunctionsStack-us-east-1",
                   env=core.Environment(account=os.getenv(
                       'CDK_DEFAULT_ACCOUNT'), region="us-east-1"),
                   lambda_role_name="lambdaroleuseast1", lambda_role_id="lambdaroleiduseast1", trigger_role_name="triggerroleuseast1", trigger_role_id="triggerroleiduseast1", region="us-east-1"
                   )

StepFunctionsStack(app, "StepFunctionsStack-us-west-2",
                   env=core.Environment(account=os.getenv(
                       'CDK_DEFAULT_ACCOUNT'), region="us-west-2"),
                   lambda_role_name="lambdaroleuswest2", lambda_role_id="lambdaroleiduswest2", trigger_role_name="triggerroleuswest2", trigger_role_id="triggerroleiduswest2", region="us-west-2"
                   )

app.synth()
