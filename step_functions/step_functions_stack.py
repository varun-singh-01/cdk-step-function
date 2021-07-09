from aws_cdk import (core as cdk,
                     aws_iam,
                     aws_lambda as _lambda,
                     aws_stepfunctions as sfn,
                     aws_stepfunctions_tasks as step_fn_tasks)
from aws_cdk import core

from infra.lambda_service import LambdaService
from infra.step_function_service import StepFunctionService


class StepFunctionsStack(cdk.Stack):

    def __init__(stack, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        StepFunctionsStack.create(stack)

    @ staticmethod
    def create(stack: core.Construct):

        # Lambda Role
        lambda_role = aws_iam.Role(scope=stack, id='cdk-lambda-role',
                                   assumed_by=aws_iam.ServicePrincipal(
                                       'lambda.amazonaws.com'),
                                   role_name='cdk-lambda-role',
                                   managed_policies=[
                                       aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                                           'service-role/AWSLambdaVPCAccessExecutionRole'),
                                       aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                                           'service-role/AWSLambdaBasicExecutionRole')
                                   ])

        # Define Lambda Functions
        submit_lambda = LambdaService.create_first_lambda(
            scope=stack, execution_role=lambda_role)
        get_status_lambda = LambdaService.create_second_lambda(
            scope=stack, execution_role=lambda_role)

        # Define Step Function
        state_machine = StepFunctionService.create_step_function(
            stack, submit_lambda, get_status_lambda)
