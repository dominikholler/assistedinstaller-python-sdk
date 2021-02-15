#!/usr/bin/env python3

import json
from http import HTTPStatus

import requests


# podman run -it --rm centos:8 bash
# dnf install -y 'dnf-command(copr)'
# dnf copr -y enable ocm/tools
# dnf install -y ocm-cli
# get token for ocm from https://cloud.redhat.com/openshift/token
# ocm login --token eyXXX
# ocm token

class AssistedInstaller:
    """
    API doc: https://generator.swagger.io/?url=https://raw.githubusercontent.com/openshift/assisted-service/master/swagger.yaml
    """
    token_file = 'token.txt'
    default_url = 'https://api.openshift.com/api/assisted-install/v1'

    def __init__(self, base_url=default_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers['Authorization'] = 'Bearer {}'.format(
            self._read_first_line(self.token_file))

    def _read_first_line(self, path):
        with open(path, 'r') as file:
            return file.read().splitlines()[0]

    def get(self, url_path):
        response = self.session.get(self.base_url + url_path)
        response.raise_for_status()
        if response.status_code == HTTPStatus.OK:
            return response.json()

    def get_component_versions(self):
        return self.get('/component_versions')

    def get_clusters(self):
        return self.get('/clusters')

    def get_cluster(self, cluster_id):
        return self.get('/clusters/{}'.format(cluster_id))

    def get_cluster_hosts(self, cluster_id):
        return self.get('/clusters/{}/hosts'.format(cluster_id))

    def get_host(self, cluster_id, host_id):
        return self.get('/clusters/{}/hosts/{}'.format(
            cluster_id, host_id
        ))

    def _post(self, url_path):
        response = self.session.post(self.base_url + url_path)
        response.raise_for_status()
        return response.json()

    def reset_cluster(self, cluster_id):
        url_path = '/clusters/{}/actions/reset'.format(
            cluster_id
        )
        return self._post(url_path)

    def install_cluster(self, cluster_id):
        url_path = '/clusters/{}/actions/install'.format(
            cluster_id
        )
        return self._post(url_path)

    def _patch(self, url_path, data):
        response = self.session.patch(
            url=self.base_url + url_path,
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )
        response.raise_for_status()
        # HTTPStatus.CREATED
        return response.json()

    def patch_host_installer_args(self, cluster_id, host_id, args):
        url_path = '/clusters/{}/hosts/{}/installer-args'.format(
            cluster_id, host_id
        )
        return self._patch(url_path=url_path, data={"args": args})

    def patch_cluster(self, cluster_id, attributes):
        url_path = '/clusters/{}'.format(
            cluster_id
        )
        return self._patch(url_path=url_path, data=attributes)


def get_by_name(items, value):
    return next(item for item in items if item['name'] == value)


installer = AssistedInstaller()
#
# installer = AssistedInstaller(
#     base_url='https://api.integration.openshift.com/api/assisted-install/v1'
# )

cluster = get_by_name(installer.get_clusters(), 'hcs')
# for host in installer.get_cluster_hosts(cluster_id=cluster['id']):
#     print(host['requested_hostname'])
#     print(host)


installer.patch_cluster(cluster_id=cluster['id'], attributes={
     'base_dns_domain': 'lab.eng.tlv2.redhat.com',
})

# if cluster['status'] == 'ready':

# print(installer.patch_cluster(cluster_id=cluster['id'], attributes={'vip_dhcp_allocation': True}))

# ip=<client-ip>:<srv-ip>:<gw-ip>:<netmask>:<host>:<device>:<autoconf>
# ip=10.46.8.30::10.46.11.254:255.255.252.0:nike01:eno1:off nameserver=10.46.0.31
# ip=10.46.8.31::10.46.11.254:255.255.252.0:nike02:eno1:off nameserver=10.46.0.31
# ip=10.46.8.32::10.46.11.254:255.255.252.0:nike02:eno1:off nameserver=10.46.0.31

installer_args = {
    'nike05.rhev.lab.eng.brq.redhat.com': [
        '--append-karg',
        'ip=10.37.160.71::10.37.160.254:255.255.255.0:nike05:eno1:off',
        '--append-karg',
        'nameserver=10.37.136.1',
        '--append-karg',
        'ip=eno2:off'
    ],
    'nike06.rhev.lab.eng.brq.redhat.com': [
        '--append-karg',
        'ip=10.37.160.73::10.37.160.254:255.255.255.0:nike06:eno1:off',
        '--append-karg',
        'nameserver=10.37.136.1',
        '--append-karg',
        'ip=eno2:off'
    ],
    'nike07.rhev.lab.eng.brq.redhat.com': [
        '--append-karg',
        'ip=10.37.160.75::10.37.160.254:255.255.255.0:nike07:eno1:off',
        '--append-karg',
        'nameserver=10.37.136.1',
        '--append-karg',
        'ip=eno2:off'
    ]
}

# do this manually in web ui before triggering this script
# installer_args['dhcp-8-190.lab.eng.tlv2.redhat.com'] = \
#     installer_args['nike01.lab.eng.tlv2.redhat.com']

for host in installer.get_cluster_hosts(cluster_id=cluster['id']):
    host_key = host['requested_hostname']
    print('paching {}'.format(host_key))
    installer.patch_host_installer_args(
        cluster_id=cluster['id'],
        host_id=host['id'],
        args=installer_args[host_key]
    )

# print(installer.patch_cluster(cluster_id=cluster['id'], attributes={
#     'base_dns_domain': 'lab.eng.tlv2.redhat.com',
#     'machine_network_cidr': '10.46.8.0/22'
# }))

# the web ui seems to mess up machine_network_cidr
# print(installer.install_cluster(cluster_id=cluster['id']))
