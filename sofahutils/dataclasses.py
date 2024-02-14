from typing import Optional, Union
import subprocess

class Service: 
    """
    This class is used to represent a service in the sofah context.
    """

    def __init__(self, name:str) -> None:
        """
        Constructor for the service class.
        :param name: The name of the service.
        :type name: str
        """

        self.name = name


class DockerComposeService(Service):
    """
    This class is used to represent a service in a docker-compose file.

    """

    def __init__(self, name:str, service_def:list[str], github_link:str, token:str, networks:Optional[Union[str, list[str]]] = [], variables:Optional[dict] = {}) -> None:
        """
        Constructor for the DockerComposeService class.

        The `variables` parameter is used to assign variables to the placeholders in the service_def. The dict should look like this:
        ```
        {
            "<var_name>": "value",
            "<var_name2>": 15
        }
        ```
        For an easy deployment the `github_link` parameter is used to store the link to the github repository of the service.
        The github link should look like this:
        `https://$TOKEN:x-oauth-basic@github.com/sofahd/<repo_name>.git` Where <repo_name> is the name of the repository, and `$TOKEN` is the placeholder for the oauth token.
        In this case it is expected that the token is stored in the environment, so leave the placeholder as is, and the token will be replaced at runtime.

        :param name: the name of the service
        :type name: str
        :param service_def: the service definition, this is the part of the docker-compose file that would define the service. Variables are allowed, but have to be identified by `<var_name>`
        :type service_def: list[str]
        :param networks: the networks the service should be connected to, defaults to [], otherwise it should be a list of strings
        :type networks: Optional[Union[str, list[str]]]
        :param variables: the variables to be replaced in the service_def, defaults to {}
        :type variables: Optional[dict]
        :param github_link: the link to the github repository of the service
        :type github_link: str
        :param token: the token to access the github repository
        :type token: str
        """

        super().__init__(name=name)
        self.networks = [networks] if isinstance(networks, str) else networks
        self.service_def = service_def

        self.github_link = github_link

        self.token = token

        if not isinstance(networks, list) or not all(isinstance(item, str) for item in networks):
            raise TypeError(f"ip_address must be of type str or list[str], not {type(networks)}")
        
        self.variables = variables
        
    
    def dump_to_compose(self) -> list[str]:
        """
        This method is used to dump so the service can be used in a docker-compose file
        It returns a list of strings, each string is a line in the docker-compose file
        The return will look something like this:
        ```
        service_name:
            networks:
                - network1
                - network2
            service_def
        ```
        **ATTENTION:** The service_def will have the variables replaced by their values. Also this method will not create network definitions, only network connections.
        :return: the service definition that will be used in the docker-compose file
        :rtype: list[str]
        """

        ret_list = []

        for line in self.service_def:
            for var in self.variables.keys():
                line = line.replace(var, str(self.variables[var]))
            ret_list.append(line)
        ret_list.append(f"\n")
        ret_list.insert(0, f"  {self.name}:")

        return ret_list
    
    def download_repo(self):
        """
        With this method you can download the repo containing the code for the service.
        """
    
        subprocess.run(f"git clone {self.github_link.replace('$TOKEN', self.token)}", shell=True)
    

class DockerCompose():
    """
    This class is used to represent a docker-compose file.
    """

    def __init__(self, version:Optional[str]="3.8", services:Optional[list[DockerComposeService]] = []) -> None:
        """
        Constructor for the DockerCompose class.
        :param version: Optional: the version of the docker-compose defaults to `"3.8"`
        :type version: str
        :param services: the services that are in the docker-compose file, defaults to []
        :type services: Optional[list[DockerComposeService]]
        """

        self.version = version
        self.services = services
    
    def dump(self) -> list[str]:
        """
        This method is designed to actually build the docker-compose file.
        """

        network_lines = self._build_networks()

        ret_list = [f"version: '{self.version}'", "\n"]

        self.services.sort(key=lambda x: x.name)

        for service in self.services:
            ret_list.extend(service.dump_to_compose())
        
        ret_list.extend(network_lines)

        return ret_list

    def _build_networks(self) -> list[str]:
        """
        This method is used to build the network definitions.
        """

        ret_list = []
        network_list = []

        for service in self.services:
            for network in service.networks:
                if network not in network_list:
                    network_list.append(network)

        if len(network_list) > 0:
            network_list.sort()
            ret_list.append("networks:")
            for network in network_list:
                ret_list.append(f"  {network}:")
                ret_list.append(f"    name: {network}")
                ret_list.append("    driver: bridge")


        return ret_list
        