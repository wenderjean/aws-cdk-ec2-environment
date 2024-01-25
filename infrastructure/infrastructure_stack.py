import os.path

from constructs import Construct
from aws_cdk.aws_s3_assets import Asset
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    Stack,
)

dirname = os.path.dirname(__file__)

class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC Configuration
        vpc = ec2.Vpc(self, "MyVPCName",
                      nat_gateways=0,
                      subnet_configuration=[
                          ec2.SubnetConfiguration(name="public1", subnet_type=ec2.SubnetType.PUBLIC),
                          ec2.SubnetConfiguration(name="public2", subnet_type=ec2.SubnetType.PUBLIC),
                          ec2.SubnetConfiguration(name="public3", subnet_type=ec2.SubnetType.PUBLIC)
                      ])

        # AMI Configuration
        linux = ec2.MachineImage.generic_linux({
                    'us-east-1': 'ami-058bd2d568351da34'
                })

        # Role Configuration
        role = iam.Role(self, "MyIAMRole", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))

        # KeyPair Configuration
        #
        # !! ATTENTION !!
        #
        # You should manually create the KeyPair in AWS and store .pem file somewhere to use it
        # during future SSH connections. Reference you KeyPair here using its name (key_pair_name)
        key = ec2.KeyPair.from_key_pair_attributes(self, "MyKeyPair",
                                                   key_pair_name="allow-ssh-access-key-pair",
                                                   type=ec2.KeyPairType.RSA)

        # Security Group Configuration
        security_group = ec2.SecurityGroup(self, "MySecurityGroup",
                                           vpc=vpc,
                                           allow_all_outbound=True)

        security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))
        security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))

        # EC2 Instance Configuration
        instance = ec2.Instance(self, "MyAppInstance",
                                    instance_type=ec2.InstanceType("t3.nano"),
                                    machine_image=linux,
                                    vpc=vpc,
                                    role=role,
                                    security_group=security_group,
                                    key_pair=key
                                )

        # S3 Configuration
        asset = Asset(self, "Asset", path=os.path.join(dirname, "configure.sh"))

        file_path = instance.user_data.add_s3_download_command(
            bucket=asset.bucket,
            bucket_key=asset.s3_object_key
        )

        # Executes script from S3 to provide any required customization (configure.sh)
        instance.user_data.add_execute_file_command(
            file_path=file_path
        )

        asset.grant_read(instance.role)
