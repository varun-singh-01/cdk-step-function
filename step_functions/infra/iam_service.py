from aws_cdk import (core as cdk,
                     aws_iam,
                     aws_lambda,
                     aws_stepfunctions as step_fn,
                     aws_stepfunctions_tasks as step_fn_tasks)
from aws_cdk import core


class IamService:

    @staticmethod
    def create_sfn_trigger_role(scope: core.Construct, trigger_role_name: str, trigger_role_id: str, region: str) -> aws_iam.Role:
        s3_principal = aws_iam.ServicePrincipal("s3.amazonaws.com")
        lambda_principal = aws_iam.ServicePrincipal("lambda.amazonaws.com")
        states_principal = aws_iam.ServicePrincipal("states.amazonaws.com")
        glue_principal = aws_iam.ServicePrincipal("glue.amazonaws.com")
        queue_principal = aws_iam.ServicePrincipal("sqs.amazonaws.com")

        return aws_iam.Role(
            scope=scope,
            id=trigger_role_id,
            role_name=trigger_role_name,
            assumed_by=aws_iam.CompositePrincipal(
                s3_principal, lambda_principal, glue_principal, queue_principal, states_principal),
            description="Role to trigger Step Function for region -{}".format(
                region),
            max_session_duration=None)

    @staticmethod
    def add_state_machine_policy(stepfn_arn):
        policy_statement = aws_iam.PolicyStatement()
        policy_statement.effect = aws_iam.Effect.ALLOW
        policy_statement.add_actions("states:StartExecution")
        policy_statement.add_actions("states:ListExecutions")
        policy_statement.add_resources(stepfn_arn)
        return policy_statement
