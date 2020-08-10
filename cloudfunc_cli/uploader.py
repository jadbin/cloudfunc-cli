# coding=utf-8

import sys

import tqdm
import requests
import requests_toolbelt

from .package import PackageFile


class ProgressBar(tqdm.tqdm):

    def update_to(self, n: int):
        self.update(n - self.n)


class Uploader:

    def __init__(self, url: str = None):
        self.url = url
        self.session = requests.Session()

    def upload(self, pkg: PackageFile):
        data_to_send = self._convert_metadata_to_tuples(pkg.metadata)

        print(f"Uploading {pkg.base_filename}")

        with open(pkg.filename, 'rb') as f:
            data_to_send.append(
                ('content', (pkg.base_filename, f, 'application/octet-stream'))
            )
            encoder = requests_toolbelt.MultipartEncoder(data_to_send)
            with ProgressBar(
                    total=encoder.len,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    miniters=1,
                    file=sys.stdout
            ) as bar:
                monitor = requests_toolbelt.MultipartEncoderMonitor(
                    encoder, lambda monitor: bar.update_to(monitor.bytes_read))
                resp = self.session.post(
                    self.url,
                    data=monitor,
                    headers={'Content-Type': monitor.content_type},
                )
        return resp

    def _convert_metadata_to_tuples(self, metadata: dict):
        data_to_send = []
        for k, v in metadata.items():
            if not isinstance(v, (list, tuple)):
                data_to_send.append((k, v))
            else:
                for item in v:
                    data_to_send.append((k, item))
        return data_to_send
