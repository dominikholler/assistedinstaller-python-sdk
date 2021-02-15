#!/usr/bin/env python3

from assistedinstaller import AssistedInstaller

installer = AssistedInstaller('http://192.168.178.187:8090')

print(installer.get_component_versions())