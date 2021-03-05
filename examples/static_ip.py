#!/usr/bin/env python3

from assistedinstaller import AssistedInstaller

installer = AssistedInstaller()

cluster = installer.get_by_name(installer.get_clusters(), 'hcs')



installer.patch_cluster(cluster_id=cluster['id'], attributes={
     'base_dns_domain': 'hcs.rhev.lab.eng.brq.redhat.com',
})

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



for host in installer.get_cluster_hosts(cluster_id=cluster['id']):
    host_key = host['requested_hostname']
    print('paching {}'.format(host_key))
    installer.patch_host_installer_args(
        cluster_id=cluster['id'],
        host_id=host['id'],
        args=installer_args[host_key]
    )
