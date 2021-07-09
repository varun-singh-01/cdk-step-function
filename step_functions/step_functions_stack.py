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
        # state_machine = StepFunctionService.create_step_function(
        #     stack, first_lambda, second_lambda)

        submit_job = step_fn_tasks.LambdaInvoke(stack, "Submit Job",
                                                lambda_function=submit_lambda,
                                                # Lambda's result is in the attribute `Payload`
                                                output_path="$.Payload"
                                                )

        wait_x = sfn.Wait(stack, "Wait X Seconds",
                          time=sfn.WaitTime.seconds_path("$.waitSeconds")
                          )

        get_status = step_fn_tasks.LambdaInvoke(stack, "Get Job Status",
                                                lambda_function=get_status_lambda,
                                                # Pass just the field named "guid" into the Lambda, put the
                                                # Lambda's result in a field called "status" in the response
                                                input_path="$.guid",
                                                output_path="$.Payload"
                                                )

        job_failed = sfn.Fail(stack, "Job Failed",
                              cause="AWS Batch Job Failed",
                              error="DescribeJob returned FAILED"
                              )

        final_status = step_fn_tasks.LambdaInvoke(stack, "Get Final Job Status",
                                                  lambda_function=get_status_lambda,
                                                  # Use "guid" field as input
                                                  input_path="$.guid",
                                                  output_path="$.Payload"
                                                  )

        definition = submit_job.next(wait_x).next(get_status).next(sfn.Choice(stack, "Job Complete?").when(sfn.Condition.string_equals(
            "$.status", "FAILED"), job_failed).when(sfn.Condition.string_equals("$.status", "SUCCEEDED"), final_status).otherwise(wait_x))

        sfn.StateMachine(stack, "StateMachine",
                         definition=definition,
                         timeout=cdk.Duration.seconds(30)
                         )
