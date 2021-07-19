import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as sfn_tasks
import aws_cdk.aws_lambda as lambda_
from aws_cdk import core


class StepFunctionService:

    @staticmethod
    def create_step_function(stack, first_lambda, second_lambda):

        fail = StepFunctionService.create_fail_state(stack)

        submit_job = sfn_tasks.LambdaInvoke(stack, "Submit Job",
                                            lambda_function=first_lambda,
                                            # Lambda's result is in the attribute `Payload`
                                            output_path="$.Payload"
                                            )

        wait_x = sfn.Wait(stack, "Wait X Seconds",
                          time=sfn.WaitTime.seconds_path("$.waitSeconds")
                          )

        get_status = sfn_tasks.LambdaInvoke(stack, "Get Job Status",
                                            lambda_function=second_lambda,
                                            # Pass just the field named "guid" into the Lambda, put the
                                            # Lambda's result in a field called "status" in the response
                                            output_path="$.Payload"
                                            )

        job_failed = sfn.Fail(stack, "Job Failed",
                              cause="AWS Batch Job Failed",
                              error="DescribeJob returned FAILED"
                              )

        final_status = sfn_tasks.LambdaInvoke(stack, "Get Final Job Status",
                                              lambda_function=second_lambda,
                                              # Use "guid" field as input
                                              output_path="$.Payload"
                                              )

        definition = submit_job.next(get_status).next(
            sfn.Choice(stack, "Job Complete?")
            .when(sfn.Condition.string_equals(
                  "$.status", "FAILED"), job_failed).when(sfn.Condition.string_equals("$.status", "SUCCEEDED"), final_status).otherwise(wait_x))

        sfn.StateMachine(stack, "StateMachine",
                         definition=definition,
                         timeout=core.Duration.seconds(180)
                         )

    @staticmethod
    def create_fail_state(stack):
        return sfn.Fail(scope=stack,
                        id="first_task",
                        cause="Exception Occurred",
                        error="$.error")

    @staticmethod
    def create_lambda_task(stack, task_def, task_lambda, result_key='$'):
        return sfn.Task(scope=stack,
                        id=task_def,
                        task=sfn_tasks.InvokeFunction(task_lambda),
                        result_key=result_key)

    @staticmethod
    def create_definition(stack, first_lambda_job, second_lambda_job):

        start_state = sfn.Pass(
            scope=stack,
            id="StartState",
            result_path="$.Execution")

        success = sfn.Succeed(
            scope=stack,
            id="Step Function Execution Complete."
        )

        some_flag = sfn.Choice(
            scope=stack,
            id="Check Condition")

        chain_lambdas = sfn.Chain.start(first_lambda_job).next(
            second_lambda_job).next(success)

        return chain_lambdas
