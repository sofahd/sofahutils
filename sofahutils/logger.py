from typing import Optional
import requests, json

class SofahLogger:
    """
    This class implements an easy to use logger for the sofah project.
    It uses the API implemented by the log mudule in sofah.

    """

    def __init__(self, url:str, dst_port:Optional[int] = 0) -> None:
        """
        Constructor for the SofahLogger class.
        param url: The url to log to.
        type url: str
        param dst_port: the port of the service you are logging for, Optional, defaults to 0
        type dst_port: int
        """
        resp = requests.get(f"{url}/health")
        
        if resp.text != "OK" or resp.status_code != 200:
            raise ConnectionError(f"Could not connect to {url}")
        
        self.dst_port = dst_port
        
        self.url = url


    def log(self, event_id:str, content:dict, ip:Optional[str] = '127.0.1.1', port:Optional[int] = 0) -> None:
        """
        Use this method when you want to log something but need greater freedom about the fields of the log.

        param event_id: The event_id of the log.
        type event_id: str
        param content: The content of the log.
        type content: dict
        param ip: The optional ip of the client, defaults to 127.0.1.1
        type ip: str
        param port: The optional port of the client, defaults to 0
        type port: int
        """

        self._send_log(level='log', ip=ip, port=port, content=content, event_id=event_id)


    def info(self, message:str, ip:Optional[str] = '127.0.1.1', port:Optional[int] = 0, method:Optional[str] = 'generic') -> None:
        """
        Use this method when you want to log an info message.

        param message: The message of the log.
        type message: str
        param ip: The optional ip of the client, defaults to 127.0.1.1
        type ip: str
        param port: The optional port of the client, defaults to 0
        type port: int
        param method: The optional method of the log, defaults to 'generic'
        type method: str
        """

        self._send_log(level='info', ip=ip, port=port, message=message, method=method)


    def warn(self, message:str, ip:Optional[str] = '127.0.1.1', port:Optional[int] = 0, method:Optional[str] = 'generic') -> None:
        """
        Use this method when you want to log an warn message.

        param message: The message of the log.
        type message: str
        param ip: The optional ip of the client, defaults to 127.0.1.1
        type ip: str
        param port: The optional port of the client, defaults to 0
        type port: int
        param method: The optional method of the log, defaults to 'generic'
        type method: str
        """

        self._send_log(level='warn', ip=ip, port=port, message=message, method=method)


    def error(self, message:str, ip:Optional[str] = '127.0.1.1', port:Optional[int] = 0, method:Optional[str] = 'generic') -> None:
        """
        Use this method when you want to log an error message.

        param message: The message of the log.
        type message: str
        param ip: The optional ip of the client, defaults to 127.0.1.1
        type ip: str
        param port: The optional port of the client, defaults to 0
        type port: int
        param method: The optional method of the log, defaults to 'generic'
        type method: str
        """

        self._send_log(level='error', ip=ip, port=port, message=message, method=method)


    def _send_log(self, level:str, ip:str, port:int, content:Optional[dict] = None, event_id:Optional[str] = None, message:Optional[str] = None, method:Optional[str] = None) -> None:
        """
        This method sends the log to the API.
        Choose the level between 'info', 'warn', 'error' and 'log'.
        Keep in mind, that only the `log` level requires the `content` and `event_id` parameters , but NOT the `message` or `method` parameter.
        The other levels require the `message` and `method` parameters, but NOT the `content` or `event_id` parameter.
        param level: The level of the log, must be one of 'info', 'warn', 'error' or 'log'.
        type level: str
        param ip: The ip of the client.
        type ip: str
        param port: The port of the client.
        type port: int
        param content: Optional, only when level is 'log'. The content of the log.
        type content: dict
        param event_id: Optional, only when level is 'log'. The event_id of the log.
        type event_id: str
        param message: Optional, only when level is 'info', 'warn' or 'error'. The message of the log.
        type message: str
        param method: Optional, only when level is 'info', 'warn' or 'error'. The method of the log.
        type method: str
        """
        if level not in ['info', 'warn', 'error', 'log']:
            raise ValueError("The level must be one of 'info', 'warn', 'error' or 'log'")
        
        if (level == 'log' and not content) or (level == 'log' and not event_id):
            raise ValueError("The level 'log' requires the content and event_id parameter")
        
        if (level in ['info', 'warn', 'error'] and not message) or (level in ['info', 'warn', 'error'] and not method):
            raise ValueError(f"The level '{level}' requires the message and method parameter")

        if level not in ['info', 'warn', 'error']:
            url = self.url + "/log"
            data = {
                "eventid": event_id,
                "content": json.dumps(content),
                "ip": ip,
                "src_port": port,
                "dst_port": self.dst_port
            }
            resp = requests.post(url, data=data)

        else:
            url = f"{self.url}/{level}"
            data = {
                "message": message,
                "method": method,
                "ip": ip,
                "src_port": port,
                "dst_port": self.dst_port
            }
            resp = requests.post(url, data=data)
        
        if resp.status_code != 200:
            raise Exception(f"Failed to log message: {resp.json()}")
        
        return resp.json()