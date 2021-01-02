from aws_cdk.aws_ec2 import RouterType, CfnSecurityGroup

# basic VPC configs
VPC = 'custom-vpc'

INTERNET_GATEWAY = 'internet-gateway'

KEY_PAIR_NAME = 'us-east-1-key'

REGION = 'us-east-1'

# route tables
PUBLIC_ROUTE_TABLE = 'public-route-table'

ROUTE_TABLES_ID_TO_ROUTES_MAP = {
    PUBLIC_ROUTE_TABLE: [
        {
            'destination_cidr_block': '0.0.0.0/0',
            'gateway_id': INTERNET_GATEWAY,
            'router_type': RouterType.GATEWAY
        }
    ],
}

# security groups
SECURITY_GROUP = 'wordpress'

SECURITY_GROUP_ID_TO_CONFIG = {
    SECURITY_GROUP: {
        'group_description': 'SG of the Wordpress servers',
        'group_name': SECURITY_GROUP,
        'security_group_ingress': [
            CfnSecurityGroup.IngressProperty(
                ip_protocol='TCP', cidr_ip='0.0.0.0/0', from_port=80, to_port=80
            ),
            CfnSecurityGroup.IngressProperty(
                ip_protocol='TCP', cidr_ipv6='::/0', from_port=80, to_port=80
            ),
            CfnSecurityGroup.IngressProperty(
                ip_protocol='TCP', cidr_ip='0.0.0.0/0', from_port=443, to_port=443
            ),
            CfnSecurityGroup.IngressProperty(
                ip_protocol='TCP', cidr_ipv6='::/0', from_port=443, to_port=443
            ),
            CfnSecurityGroup.IngressProperty(
                ip_protocol='TCP', cidr_ip='0.0.0.0/0', from_port=22, to_port=22
            ),
            CfnSecurityGroup.IngressProperty(
                ip_protocol='TCP', cidr_ipv6='::/0', from_port=22, to_port=22
            ),
        ],
        'tags': [{'key': 'Name', 'value': SECURITY_GROUP}]
    },
}

# subnets and instances
PUBLIC_SUBNET = 'public-subnet'
PRIVATE_SUBNET = 'private-subnet'

PUBLIC_INSTANCE = 'public-instance'
PRIVATE_INSTANCE = 'private-instance'

# AMI ID of the WordPress by Bitnami
AMI = 'ami-0c00935023a833df1'

SUBNET_CONFIGURATION = {
    PUBLIC_SUBNET: {
        'availability_zone': 'us-east-1a', 'cidr_block': '10.0.1.0/24', 'map_public_ip_on_launch': True,
        'route_table_id': PUBLIC_ROUTE_TABLE,
        'instances': {
            PUBLIC_INSTANCE: {
                'disable_api_termination': False,
                'key_name': KEY_PAIR_NAME,
                'image_id': AMI,
                'instance_type': 't2.micro',
                'security_group_ids': [SECURITY_GROUP],
                'tags': [
                    {'key': 'Name', 'value': PUBLIC_INSTANCE},
                ],
            },
        }
    },
    PRIVATE_SUBNET: {
        'availability_zone': 'us-east-1b', 'cidr_block': '10.0.2.0/24', 'map_public_ip_on_launch': True,
        'route_table_id': PUBLIC_ROUTE_TABLE,
        'instances': {
            PRIVATE_INSTANCE: {
                'disable_api_termination': False,
                'key_name': KEY_PAIR_NAME,
                'image_id': AMI,
                'instance_type': 't2.micro',
                'security_group_ids': [SECURITY_GROUP],
                'tags': [
                    {'key': 'Name', 'value': PRIVATE_INSTANCE},
                ],
            },
        }
    }
}
