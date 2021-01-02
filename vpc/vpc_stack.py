from aws_cdk import core
from aws_cdk.aws_ec2 import Vpc, CfnRouteTable, RouterType, CfnRoute, CfnInternetGateway, CfnVPCGatewayAttachment, \
    CfnSubnet, CfnSubnetRouteTableAssociation, CfnSecurityGroup, CfnInstance

from . import config


class VpcStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create VPC
        self.bifrost_vpc = Vpc(
            self, config.VPC, cidr='10.0.0.0/16', nat_gateways=0, subnet_configuration=[], enable_dns_support=True,
            enable_dns_hostnames=True,
        )

        self.internet_gateway = self.attach_internet_gateway()

        self.subnet_id_to_subnet_map = {}
        self.route_table_id_to_route_table_map = {}
        self.security_group_id_to_group_map = {}
        self.instance_id_to_instance_map = {}

        self.create_route_tables()
        self.create_security_groups()

        self.create_subnets()
        self.create_subnet_route_table_associations()

        self.create_routes()
        self.create_instances()

    def create_route_tables(self):
        """ Create Route Tables """
        for route_table_id in config.ROUTE_TABLES_ID_TO_ROUTES_MAP:
            self.route_table_id_to_route_table_map[route_table_id] = CfnRouteTable(
                self, route_table_id, vpc_id=self.bifrost_vpc.vpc_id, tags=[{'key': 'Name', 'value': route_table_id}]
            )

    def create_routes(self):
        """ Create routes of the Route Tables """
        for route_table_id, routes in config.ROUTE_TABLES_ID_TO_ROUTES_MAP.items():
            for i in range(len(routes)):
                route = routes[i]

                kwargs = {
                    **route,
                    'route_table_id': self.route_table_id_to_route_table_map[route_table_id].ref,
                }

                if route['router_type'] == RouterType.GATEWAY:
                    kwargs['gateway_id'] = self.internet_gateway.ref

                del kwargs['router_type']

                CfnRoute(self, f'{route_table_id}-route-{i}', **kwargs)

    def attach_internet_gateway(self) -> CfnInternetGateway:
        """ Create and attach internet gateway to the VPC """
        internet_gateway = CfnInternetGateway(self, config.INTERNET_GATEWAY)
        CfnVPCGatewayAttachment(self, 'internet-gateway-attachment', vpc_id=self.bifrost_vpc.vpc_id,
                                internet_gateway_id=internet_gateway.ref)

        return internet_gateway

    def create_subnets(self):
        """ Create subnets of the VPC """
        for subnet_id, subnet_config in config.SUBNET_CONFIGURATION.items():
            subnet = CfnSubnet(
                self, subnet_id, vpc_id=self.bifrost_vpc.vpc_id, cidr_block=subnet_config['cidr_block'],
                availability_zone=subnet_config['availability_zone'], tags=[{'key': 'Name', 'value': subnet_id}],
                map_public_ip_on_launch=subnet_config['map_public_ip_on_launch'],
            )

            self.subnet_id_to_subnet_map[subnet_id] = subnet

    def create_subnet_route_table_associations(self):
        """ Associate subnets with route tables """
        for subnet_id, subnet_config in config.SUBNET_CONFIGURATION.items():
            route_table_id = subnet_config['route_table_id']

            CfnSubnetRouteTableAssociation(
                self, f'{subnet_id}-{route_table_id}', subnet_id=self.subnet_id_to_subnet_map[subnet_id].ref,
                route_table_id=self.route_table_id_to_route_table_map[route_table_id].ref
            )

    def create_security_groups(self):
        """ Creates all the security groups """
        for security_group_id, sg_config in config.SECURITY_GROUP_ID_TO_CONFIG.items():
            self.security_group_id_to_group_map[security_group_id] = CfnSecurityGroup(
                self, security_group_id, vpc_id=self.bifrost_vpc.vpc_id, **sg_config
            )

    def create_instances(self):
        """ Creates all EC2 instances """
        for subnet_id, subnet_config in config.SUBNET_CONFIGURATION.items():
            subnet = self.subnet_id_to_subnet_map[subnet_id]

            self.create_instances_for_subnet(subnet, subnet_config.get('instances', {}))

    def create_instances_for_subnet(self, subnet: CfnSubnet, instance_id_to_config_map: {str: dict}):
        """ Creates EC2 instances in a subnet """
        for instance_id, instance_config in instance_id_to_config_map.items():
            instance = self.create_instance(subnet, instance_id, instance_config)
            self.instance_id_to_instance_map[instance_id] = instance

    def create_instance(self, subnet: CfnSubnet, instance_id: str, instance_config: dict) \
            -> CfnInstance:
        """ Creates a single EC2 instance """
        security_group_ids = instance_config['security_group_ids']
        del instance_config['security_group_ids']

        return CfnInstance(self, f'{instance_id}-instance', **{
            **instance_config,
            'subnet_id': subnet.ref,
            'security_group_ids': [
                self.security_group_id_to_group_map[security_group_id].ref
                for security_group_id in security_group_ids
            ],
        })
