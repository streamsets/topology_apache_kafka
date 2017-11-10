# -*- coding: utf-8 -*-
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

import logging
import tempfile
import yaml
from socket import getfqdn, socket

from clusterdock.models import Cluster, Node
from clusterdock.utils import wait_for_condition

DEFAULT_NAMESPACE = 'clusterdock'

logger = logging.getLogger('clusterdock.{}'.format(__name__))


def main(args):
    # Image name
    image = '{}/{}/topology_apache_kafka:kafka-{}-{}'.format(args.registry,
                                                             args.namespace or DEFAULT_NAMESPACE,
                                                             args.kafka_version,
                                                             args.scala_version)

    # Nodes in the Kafka cluster
    nodes = [Node(hostname=hostname,
                  group='brokers',
                  ports=[2181, 9092],
                  image=image)
             for hostname in args.brokers]

    cluster = Cluster(*nodes)
    cluster.start(args.network, pull_images=args.always_pull)

    # TODO: Add support for cluster mode (e.g. all nodes are part of the same cluster). Today we only
    # start each node independently so they will all end up independent one-node clusters.

    for node in cluster:
        node.execute('/kafka/bin/zookeeper-server-start.sh /kafka/config/zookeeper.properties &', detach=True)
        node.execute('/kafka/bin/kafka-server-start.sh /kafka/config/server.properties &', detach=True)
