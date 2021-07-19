from aws_cdk import (core as cdk,
                     aws_iam,
                     aws_lambda,
                     aws_stepfunctions as step_fn,
                     aws_stepfunctions_tasks as step_fn_tasks)
from aws_cdk import core


class LambdaService:

    @staticmethod
    def create_first_lambda(scope: core.Construct, execution_role: aws_iam.Role) -> aws_lambda.Function:
        _lambda = aws_lambda.Function(scope=scope,
                                      id="first_lambda_function",
                                      function_name="first_lambda_function",
                                      handler='first_lamda_handler.handler',
                                      runtime=aws_lambda.Runtime.PYTHON_3_7,
                                      code=aws_lambda.Code.asset(
                                          'step_functions/infra/lambda/first_lambda'),
                                      role=execution_role,
                                      timeout=cdk.Duration.seconds(25)
                                      )

        return _lambda

    @staticmethod
    def create_second_lambda(scope: core.Construct, execution_role: aws_iam.Role) -> aws_lambda.Function:
        _lambda = aws_lambda.Function(scope=scope,
                                      id="second_lambda_function",
                                      function_name="second_lambda_function",
                                      handler='second_lamda_handler.handler',
                                      runtime=aws_lambda.Runtime.PYTHON_3_7,
                                      code=aws_lambda.Code.asset(
                                          'step_functions/infra/lambda/second_lambda'),
                                      role=execution_role,
                                      timeout=cdk.Duration.seconds(25)
                                      )
        return _lambda

    @staticmethod
    def create_lambda_trigger(scope: core.Construct, execution_role: aws_iam.Role, state_machine_arn) -> aws_lambda.Function:
        _lambda = aws_lambda.Function(scope=scope,
                                      id="run_sfn_lambda",
                                      function_name="run_sfn",
                                      handler='run_sfn.handler',
                                      runtime=aws_lambda.Runtime.PYTHON_3_7,
                                      code=aws_lambda.Code.asset(
                                          'step_functions/infra/lambda/trigger'),
                                      role=execution_role,
                                      timeout=None
                                      )
        _lambda.add_environment(
            'STATE_MACHINE_ARN', state_machine_arn)

        return _lambda
