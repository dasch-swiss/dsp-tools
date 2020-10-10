import requests
from .helpers import BaseError

class Sipi:
    def __init__(self, sipiserver: str, token: str):
        self.sipiserver = sipiserver
        self.token = token

    def on_api_error(self, res):
        """
        Method to check for any API errors
        :param res: The input to check, usually JSON format
        :return: Possible KnoraError that is being raised
        """

        if res.status_code != 200:
            raise BaseError("SIPI-ERROR: status code=" + str(res.status_code) + "\nMessage:" + res.text)

        if 'error' in res:
            raise BaseError("SIPI-ERROR: API error: " + res.error)

    def upload_image(self, filepath):
        files = {
            'file': (filepath, open(filepath, 'rb')),
        }
        req = requests.post(self.sipiserver + "/upload?token=" + self.token,
                            files=files)
        self.on_api_error(req)
        res = req.json()
        return res
