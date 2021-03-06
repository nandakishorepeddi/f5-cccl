#!/usr/bin/env python
# Copyright (c) 2017,2018, F5 Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json
import pytest

from f5_cccl.api import F5CloudServiceManager
from f5_cccl.exceptions import F5CcclConfigurationReadError
from f5_cccl.resource import ltm
from f5_cccl.resource.ltm.virtual import ApiVirtualServer
from f5_cccl.service.manager import ServiceConfigDeployer
from f5_cccl.service.config_reader import ServiceConfigReader

from mock import MagicMock
from mock import Mock
from mock import patch

class TestServiceConfigReader:

    def setup(self):
        self.partition = "Test"

        svcfile_ltm = 'f5_cccl/schemas/tests/ltm_service.json'
        with open(svcfile_ltm, 'r') as fp:
            self.ltm_service = json.loads(fp.read())
        svcfile_net = 'f5_cccl/schemas/tests/net_service.json'
        with open(svcfile_net, 'r') as fp:
            self.net_service = json.loads(fp.read())

    def test_create_reader(self):
        reader = ServiceConfigReader(
            self.partition)

        assert reader
        assert reader._partition == self.partition

    def test_get_config(self):
        reader = ServiceConfigReader(self.partition)
        config = reader.read_ltm_config(self.ltm_service, 0,
                                        'marathon-bigip-ctlr-v1.2.1')

        assert len(config.get('virtuals')) == 2
        assert len(config.get('pools')) == 1
        assert len(config.get('http_monitors')) == 1
        assert len(config.get('https_monitors')) == 1
        assert len(config.get('icmp_monitors')) == 1
        assert len(config.get('tcp_monitors')) == 1
        assert len(config.get('l7policies')) == 3
        assert len(config.get('iapps')) == 1

        config = reader.read_net_config(self.net_service, 0)
        assert len(config.get('arps')) == 1
        assert len(config.get('fdbTunnels')) == 1
        assert len(config.get('userFdbTunnels')) == 1

    def test_create_config_item_exception(self):

        with patch.object(ApiVirtualServer, '__init__', side_effect=ValueError("test exception")):
            reader = ServiceConfigReader(self.partition)
            with pytest.raises(F5CcclConfigurationReadError) as e:
                reader.read_ltm_config(self.ltm_service, 0,
                                       'marathon-bigip-ctlr-v1.2.1')
