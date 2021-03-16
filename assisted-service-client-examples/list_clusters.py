import assisted_service_client


def _read_first_line(path):
    with open(path, 'r') as file:
        return file.read().splitlines()[0]


config = assisted_service_client.Configuration()
config.host = "https://api.openshift.com/api/assisted-install/v1"
config.api_key['Authorization'] = _read_first_line('token.txt')
config.api_key_prefix['Authorization'] = 'Bearer'

# config.debug = True
api = assisted_service_client.ApiClient(configuration=config)
installer = assisted_service_client.InstallerApi(api_client=api)

print(installer.list_clusters())

