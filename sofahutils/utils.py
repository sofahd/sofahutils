from .logger import SofahLogger
from typing import Union
import requests
"""
This file is used to make a ton of useful utility-functions available to the user.
"""

def get_own_ip(api_list:Union[list[str]], logger:SofahLogger) -> str:
    """
    This function makes a http request to one of a few submitted apis to get the own ip.
    :param api_list: expects a config to get the urls
    :type api_list: list[str] or str
    :param logger: The Logger object to allow this helper function to work with logging aswell.
    :type logger: SofahLogger
    :return: str of ip if successful, `127.0.0.1` if not
    """

    ret_value = "127.0.0.1"

    api_list = [api_list] if isinstance(api_list, str) else api_list

    for url in api_list:
        try: 
            response = requests.get(url,timeout=5)
            response.raise_for_status()
            ret_value = response.text
            break
        except Exception as e:
            if logger != None:
                logger.warn(f"Could not reach endpoint: {url} because Error {str(e)}", 'sofahutils.get_own_ip')
            pass
    return ret_value