#!/usr/bin/env python3

import json
from functools import wraps
from http import HTTPStatus

import requests


def _inspect_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        _check_for_error(response)
        response.raise_for_status()
        return response.json()
    return wrapper


# podman run -it --rm centos:8 bash
# dnf install -y 'dnf-command(copr)' &&  dnf copr -y enable ocm/tools && dnf install -y ocm-cli
# get token for ocm from https://cloud.redhat.com/openshift/token
# ocm login --token eyXXX
# ocm token

class AssistedInstaller:
    """
    API doc:
    https://generator.swagger.io/?url=https://raw.githubusercontent.com/openshift/assisted-service/master/swagger.yaml
    https://api.openshift.com/?urls.primaryName=assisted-service%20service
    """
    token_file = 'token.txt'
    default_domain = 'https://api.openshift.com'
    default_root = '/api/assisted-install/v1'
    content_type_json = {'content-type': 'application/json'}

    def __init__(self, domain=default_domain, root=default_root):
        self.base_url = domain + root
        self.session = requests.Session()
        self.session.headers['Authorization'] = 'Bearer {}'.format(
            _read_first_line(self.token_file))
        self.events_shown = set()

    def get_by_name(self, items, value):
        return next(item for item in items if item['name'] == value)

    def get_component_versions(self):
        return self._get('/component_versions')

    def get_clusters(self):
        return self._get('/clusters')

    def get_cluster(self, cluster_id):
        return self._get('/clusters/{}'.format(cluster_id))

    def create_cluster(self, **attributes):
        return self._post('/clusters', data=attributes)

    def patch_cluster(self, cluster_id, **attributes):
        url_path = f'/clusters/{cluster_id}'
        return self._patch(url_path=url_path, data=attributes)

    def get_cluster_hosts(self, cluster_id):
        return self._get('/clusters/{}/hosts'.format(cluster_id))

    def reset_cluster(self, cluster_id):
        url_path = f'/clusters/{cluster_id}/actions/reset'
        return self._post(url_path)

    def install_cluster(self, cluster_id):
        url_path = f'/clusters/{cluster_id}/actions/install'
        return self._post(url_path)

    def get_cluster_events(self, cluster_id):
        return self._get(f'/clusters/{cluster_id}/events')

    def print_new_events(self, cluster_id):
        for event in self.get_cluster_events(cluster_id):
            hash_event = hash(frozenset(event.items()))
            if hash_event not in self.events_shown:
                self.events_shown.add(hash_event)
                print(event)

    def get_host(self, cluster_id, host_id):
        return self._get(f'/clusters/{cluster_id}/hosts/{host_id}')

    def get_host_ignition(self, cluster_id, host_id):
        return self._get(f'/clusters/{cluster_id}/hosts/{host_id}/ignition')

    def create_downloads_image(self, cluster_id, **kwargs):
        return self._post(
            f'/clusters/{cluster_id}/downloads/image',
            data=kwargs
        )

    def get_downloads_image(self, cluster_id):
        return self._get(
            f'/clusters/{cluster_id}/downloads/image'
        )

    @_inspect_response
    def _get(self, url_path):
        return self.session.get(self.base_url + url_path)

    @_inspect_response
    def _post(self, url_path, data=None):
        return self.session.post(
            self.base_url + url_path,
            data=json.dumps(data),
            headers=self.content_type_json
        )

    @_inspect_response
    def _patch(self, url_path, data):
        return self.session.patch(
            url=self.base_url + url_path,
            data=json.dumps(data),
            headers=self.content_type_json
        )

    def patch_host_installer_args(self, cluster_id, host_id, args):
        url_path = '/clusters/{}/hosts/{}/installer-args'.format(
            cluster_id, host_id
        )
        return self._patch(url_path=url_path, data={"args": args})

    def get_supported_operators(self):
        return self._get('/supported-operators')


def _read_first_line(path):
    with open(path, 'r') as file:
        return file.read().splitlines()[0]


def _check_for_error(response):
    if not response.ok:
        try:
            print(response.json())
        except ValueError:
            pass
