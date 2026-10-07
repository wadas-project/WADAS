# This file is part of WADAS project.
#
# WADAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WADAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WADAS. If not, see <https://www.gnu.org/licenses/>.
#
# Author(s): Stefano Dell'Osa, Alessandro Palla, Cesare Di Mauro, Antonio Farina
# Date: 2024-10-20
# Description: Mqtt Broker

import asyncio
import datetime
import logging
import threading

from amqtt.broker import Broker
from amqtt.client import MQTTClient
from amqtt.mqtt.constants import QOS_1

logger = logging.getLogger(__name__)


class MqttBroker:
    """Class to handle communication with actuators via MQTT protocol"""

    broker = None

    def __init__(
        self,
        ip: str,
        port: int,
        ssl_certificate: str,
        ssl_key: str,
        subscribe_topics=None,
        receiver_callback=None,
        actuator_timeout_threshold=30,
    ):

        self.ip = ip
        self.port = port
        self.ssl_certificate = ssl_certificate
        self.ssl_key = ssl_key
        self.startup_time = None
        self.startup_error = None
        self.loop = None
        self.thread = None
        self.amqtt_broker = None
        self.started = threading.Event()
        self.client = None
        self.receiver_callback = receiver_callback
        self.subscribed_topics = subscribe_topics

        self.config = {
            "listeners": {
                "default": {
                    "type": "tcp",
                    "bind": f"{self.ip}:{self.port}",
                    "ssl": True,
                    "certfile": self.ssl_certificate,
                    "keyfile": self.ssl_key,
                }
            },
            "sys_interval": 10,
            "auth": {
                "allow-anonymous": True,
            },
        }

        logger.info("Created MqttBroker")

    def set_subscribed_topics(self, topics):
        self.subscribed_topics = topics

    async def _start_broker(self):
        """Method to start the MQTT broker"""
        self.amqtt_broker = Broker(self.config)
        await self.amqtt_broker.start()
        client_config = {
            "check_hostname": False,
            "verify_cert": False,
        }

        self.client = MQTTClient(config=client_config)

        await self.client.connect(f"mqtts://127.0.0.1:{self.port}")

        if self.subscribed_topics:
            tuples = [(topic, QOS_1) for topic in self.subscribed_topics]
            await self.client.subscribe(tuples)

            logger.info(f"Subscribed to {', '.join(self.subscribed_topics)}")
        else:
            logger.info("No topic to subscribe")

    def _run(self):
        """Method to start both the MQTT broker and the WADAS MQTT Client (acting like a server)"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_until_complete(self._start_broker())

            self.receiver_task = self.loop.create_task(self._receiver())

            self.thread.started_successfully = True
            self.started.set()

            self.loop.run_forever()

        except Exception as e:
            self.thread.startup_error = e

            logger.exception(f"Unable to start MQTT broker: " f"{type(e).__name__}: {e}")

            self.started.set()

        finally:
            if self.loop.is_running():
                self.loop.stop()

            self.loop.close()

    def run(self):
        self.started.clear()

        self.thread = threading.Thread(target=self._run, daemon=True)

        self.thread.started_successfully = False
        self.thread.startup_error = None

        self.thread.start()

        self.startup_time = datetime.datetime.now()

        self.started.wait()

        return self.thread

    async def _receiver(self):
        """Method to receive a message from one of the subscribed topics,
        the message is handled by the callback function"""
        while True:
            message = await self.client.deliver_message()

            if self.receiver_callback:
                self.receiver_callback(message)

            logger.info(f"Received message: {message.data}")

    def publish_message(self, topic, message):
        """Wrap to _publish_message method"""
        future = asyncio.run_coroutine_threadsafe(self._publish_message(topic, message), self.loop)

        return future.result()

    async def _publish_message(self, topic, message):
        """Method to publish a message on an MQTT topic"""
        await self.client.publish(topic, message.encode(), qos=QOS_1)

        logger.info("Published message %s to %s", message, topic)

    def stop(self):
        if self.loop is None:
            return

        future = asyncio.run_coroutine_threadsafe(self._stop_broker(), self.loop)

        future.result()

        self.loop.call_soon_threadsafe(self.loop.stop)

        self.thread.join()
        logger.info("MqttBroker stopped")

    async def _stop_broker(self):
        if self.amqtt_broker is not None:
            await self.amqtt_broker.shutdown()

    def serialize(self):
        """Method to serialize MqttBroker object."""
        return {
            "ssl_certificate": self.ssl_certificate,
            "ssl_key": self.ssl_key,
            "ip": self.ip,
            "port": self.port,
            "actuator_timeout_threshold": 30,
        }

    @staticmethod
    def deserialize(data):
        """Method to deserialize MqttBroker from file."""
        return MqttBroker(**data)
