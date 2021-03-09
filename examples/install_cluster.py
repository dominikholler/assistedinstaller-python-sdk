#!/usr/bin/env python3

import time

from assistedinstaller import AssistedInstaller

installer = AssistedInstaller()

ssh_public_key = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDXi1ndSgGeVrrwYiEUJpntj1e3EjKaahSPnDIrBCxo3SS677DfFHB7KQ0hg0d0X7gysh4zx/ZmucH8w1Tmd7lYlFptWw8ULrDc2+9tP688dl6E5uzjQqtv+eghkXkKL7hhkyrpIdtRWO4Nl8CBm2ECtLqr7lXYL9jwU+BKYP+dm47DQVQy1MFFA5GhCIX+mV7Oa8p8g2tJ3CBmkNKkPYAQFhrVoRnynMQFT1u0LpxLoYS8z7koArPkjClU/Sg9q5T35AlYBGBTQxA71y15eHcf2cfpGYZVgNkIjEoucPBVmKbsZscyTAjl1ejie0w2en8FTfJf6rvTpkvwgQD4hR/JqwbSUBtE+14RY53xDV79dbDT3uvpbxmD9AJwlJYoB8cSMKa7bPRyWLsKms+L/CSdVI9+2Bpae5tKTKVbcZslVGcuCw2yqnZcNI92LgyTmo+P4/WSoHlE0iqqk8GppUGg5+VlW5AktZrsAwGbs0IFm8+R/bw6xoU6sMzgWjTXVn8= dominik@t460p'
pull_secret =  'get it from https://cloud.redhat.com/openshift/create/local'
cluster_name = 'automated'
machine_network_cidr = '192.168.4.0/24'
base_dns_domain = 'ai.vlan'


def wait_for_cluster(cluster_id, success_criteria):
    cluster = installer.get_cluster(cluster_id)
    while not success_criteria(cluster):
        print(cluster['status_info'])
        installer.print_new_events(cluster_id)
        time.sleep(60)
        cluster = installer.get_cluster(cluster_id)


cluster_id = installer.create_cluster(
    name=cluster_name,
    pull_secret=pull_secret,
    openshift_version='4.7',
    base_dns_domain=base_dns_domain
).get('id')

image = installer.create_downloads_image(cluster_id, ssh_public_key=ssh_public_key)

print(image['image_info']['download_url'])

# cluster_id = installer.get_by_name(
#     installer.get_clusters(),
#     cluster_name
# )._get('id')

wait_for_cluster(
    cluster_id,
    lambda cluster: len(installer.get_cluster_hosts(cluster_id=cluster['id'])) >= 3
)

installer.patch_cluster(
    cluster_id,
    machine_network_cidr=machine_network_cidr
)

wait_for_cluster(
    cluster_id,
    lambda cluster: cluster['status'] == 'ready'
)

installer.install_cluster(cluster_id)

wait_for_cluster(
    cluster_id,
    lambda cluster: cluster['status'] == 'installed'
)
