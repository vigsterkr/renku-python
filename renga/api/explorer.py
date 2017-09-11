# -*- coding: utf-8 -*-
#
# Copyright 2017 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Client for the explorer service."""


class ExplorerApiMixin(object):
    """Client for handling storage buckets."""

    def list_buckets(self):
        """Return a list of buckets."""
        resp = self.get(
            self._url('/api/explorer/storage/bucket'),
            headers=self.headers, )

        # parse each bucket JSON and flatten
        if resp.status_code == 200:
            buckets = [_flatten_bucket(bucket) for bucket in resp.json()]
            return buckets
        else:
            return []

    def get_bucket(self, bucket_id):
        """Retrieve a bucket using the Explorer."""
        resp = self.get(
            self._url('/api/explorer/storage/bucket/{0}'.format(bucket_id)),
            headers=self.headers, )
        if resp.status_code == 200:
            return _flatten_bucket(resp.json())
        else:
            return {}


def _flatten_bucket(bucket_json):
    """Flatten the nested json structure returned by the Explorer."""
    bucket = {'id': bucket_json['id'], 'properties': {}}
    for prop in bucket_json['properties']:
        if prop['cardinality'] == 'single':
            vals = prop['values'][0]['value']
        elif prop['cardinality'] == 'set':
            vals = {v['value'] for v in prop['values']}
        elif prop['cardinality'] == 'list':
            vals = [v['value'] for v in prop['values']]
        else:
            raise RuntimeError('Undefined property cardinality')
        bucket['properties'][prop['key']] = vals
    return bucket