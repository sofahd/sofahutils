from typing import Optional, Union  

class Service: 
    """
    This class is used to represent a service in the sofah context.
    """

    def __init__(self, name:str) -> None:
        """
        Constructor for the service class.
        param name: The name of the service.
        type name: str
        """

        self.name = name



class DockerComposeService:
    """
    This class is used to represent a service in a docker-compose file.
    """

    def __init__(self, name:str, networks:Optional[Union[str, list[str]]]) -> None:
        """
        Constructor for the DockerComposeService class.

        """

        self.name = name
        self.networks = [networks] if isinstance(networks, str) else networks

        if not isinstance(networks, list) or not all(isinstance(item, str) for item in networks):
            raise TypeError(f"ip_address must be of type str or list[str], not {type(networks)}")
        
    
    def dump_to_compose(self) -> dict:
        """
        This method is used to dump so the service can be used in a docker-compose file
        """

        