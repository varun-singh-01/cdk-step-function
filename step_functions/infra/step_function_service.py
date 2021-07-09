import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as sfn_tasks
import aws_cdk.aws_lambda as lambda_
from aws_cdk import core


class StepFunctionService:

    @staticmethod
    def create_step_function(stack, first_lambda, second_lambda):

        fail = StepFunctionService.create_fail_state(stack)

        # Task 1
        first_lambda_job = sfn_tasks.LambdaInvoke(
            scope=stack,
            id="Invoke 1st Lambda",
            lambda_function=first_lambda,
            output_path='$.Payload'
        )

        # Task 2
        second_lambda_job = sfn_tasks.LambdaInvoke(
            scope=stack,
            id="Invoke 2nd Lambda",
            lambda_function=second_lambda,
            output_path='$.Payload'
        )

        definition = StepFunctionService.create_definition(
            stack=stack,
            first_lambda_job=first_lambda,
            second_lambda_job=second_lambda)

        sfn.StateMachine(
            stack, "StateMachine",
            id="My State Machine",
            definition=definition,
            timeout=core.Duration.seconds(30),
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
