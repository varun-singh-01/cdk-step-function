from aws_cdk import (core as cdk,
                     aws_iam,
                     aws_lambda as _lambda,
                     aws_stepfunctions as sfn,
                     aws_stepfunctions_tasks as step_fn_tasks)
from aws_cdk import core

from infra.lambda_service import LambdaService
from infra.iam_service import IamService
from infra.step_function_service import StepFunctionService


class StepFunctionsStack(cdk.Stack):

    def __init__(stack, scope: cdk.Construct, construct_id: str, lambda_role_name, lambda_role_id, trigger_role_name, trigger_role_id, region, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        StepFunctionsStack.create(
            stack, lambda_role_name, lambda_role_id, trigger_role_name, trigger_role_id, region)

    @ staticmethod
    def create(stack: core.Construct, lambda_role_name, lambda_role_id, trigger_role_name, trigger_role_id, region):

        print(lambda_role_name, lambda_role_id,
              trigger_role_name, trigger_role_id, region)

        # Lambda Role
        lambda_role = aws_iam.Role(scope=stack, id=lambda_role_id,
                                   assumed_by=aws_iam.ServicePrincipal(
                                       'lambda.amazonaws.com'),
                                   role_name=lambda_role_name,
                                   managed_policies=[
                                       aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                                           'service-role/AWSLambdaVPCAccessExecutionRole'),
                                       aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                                           'service-role/AWSLambdaBasicExecutionRole')
                                   ])

        # Create Trigger Role
        # trigger_role = IamService.create_sfn_trigger_role(
        #     stack, trigger_role_name, trigger_role_id, region)

        s3_principal = aws_iam.ServicePrincipal("s3.amazonaws.com")
        lambda_principal = aws_iam.ServicePrincipal("lambda.amazonaws.com")
        states_principal = aws_iam.ServicePrincipal("states.amazonaws.com")
        glue_principal = aws_iam.ServicePrincipal("glue.amazonaws.com")
        queue_principal = aws_iam.ServicePrincipal("sqs.amazonaws.com")

        trigger_role = aws_iam.Role(
            scope=stack,
            id=trigger_role_id,
            role_name=trigger_role_name,
            assumed_by=aws_iam.CompositePrincipal(
                s3_principal, lambda_principal, glue_principal, queue_principal, states_principal),
            description="Role to trigger Step Function for region",
            max_session_duration=None)

        # Define Lambda Functions
        submit_lambda = LambdaService.create_first_lambda(
            scope=stack, execution_role=lambda_role)
        get_status_lambda = LambdaService.create_second_lambda(
            scope=stack, execution_role=lambda_role)

        # Define Step Function
        # StepFunctionService.create_step_function(
        #     stack, submit_lambda, get_status_lambda)
        fail = StepFunctionService.create_fail_state(stack)

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
                                                output_path="$.Payload"
                                                )

        job_failed = sfn.Fail(stack, "Job Failed",
                              cause="AWS Batch Job Failed",
                              error="DescribeJob returned FAILED"
                              )

        final_status = step_fn_tasks.LambdaInvoke(stack, "Get Final Job Status",
                                                  lambda_function=get_status_lambda,
                                                  # Use "guid" field as input
                                                  output_path="$.Payload"
                                                  )

        definition = submit_job.next(get_status).next(
            sfn.Choice(stack, "Job Complete?")
            .when(sfn.Condition.string_equals(
                  "$.status", "FAILED"), job_failed).when(sfn.Condition.string_equals("$.status", "SUCCEEDED"), final_status).otherwise(wait_x))

        state_machine = sfn.StateMachine(stack, "StateMachine",
                                         definition=definition,
                                         timeout=core.Duration.seconds(180)
                                         )

        # Create Lambda Trigger
        trigger_lambda = LambdaService.create_lambda_trigger(
            stack, execution_role=trigger_role)
        trigger_lambda.add_to_role_policy(IamService.add_state_machine_policy(
            stepfn_arn=state_machine.state_machine_arn
        ))
