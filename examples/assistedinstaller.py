#!/usr/bin/env python3

import json
from http import HTTPStatus

import requests


# sudo podman run -it --rm centos:8 bash
# dnf install -y 'dnf-command(copr)' &&  dnf copr -y enable ocm/tools && dnf install -y ocm-cli
# get token for ocm from https://cloud.redhat.com/openshift/token
# ocm login --token eyXXX
# ocm token

class AssistedInstaller:
    """
    API doc: https://generator.swagger.io/?url=https://raw.githubusercontent.com/openshift/assisted-service/master/swagger.yaml
    """
    token_file = 'token.txt'
    default_domain = 'https://api.openshift.com'
    default_root = '/api/assisted-install/v1'

    def __init__(self, domain=default_domain, root=default_root):
        self.base_url = domain + root
        self.session = requests.Session()
        self.session.headers['Authorization'] = 'Bearer {}'.format(
            self._read_first_line(self.token_file))

    def _read_first_line(self, path):
        with open(path, 'r') as file:
            return file.read().splitlines()[0]
        
    def get_by_name(self, items, value):
        return next(item for item in items if item['name'] == value)

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

    def get_supported_operators(self):
        return self.get('/supported-operators')

