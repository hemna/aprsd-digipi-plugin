import time
import logging

from aprsd import packets, plugin, utils
from aprsd.packets import log as packet_log
from aprsd.packets import collector as packet_collector
from aprsd.stats import collector
from aprsd.threads.aprsd import APRSDThread
from aprsd.utils import objectstore
from loguru import logger
from oslo_config import cfg

import aprsd_digipi_plugin
from aprsd_digipi_plugin import conf  # noqa

CONF = cfg.CONF
LOG = logging.getLogger("APRSD")
LOGU = logger


@utils.singleton
class DigipiStats(objectstore.ObjectStoreMixin):
    # We won't try and store more than this number
    # of packets in the class/file
    max_packet_length = 100
    data: dict = {
        'rx': 0,
        'packets': [],
    }
    def rx(self, packet):
        if isinstance(packet, packets.GPSPacket):
            comment = packet.comment
            if comment and 'digipi' in comment.lower():
               self.data['rx'] += 1
               # Try and keep the packet list to a reasonable number
               if len(self.data['packets']) >= self.max_packet_length:
                   self.data['packets'].pop()
               self.data['packets'].append(packet)

    def tx(self, packet):
        pass

    def load(self):
        pass

    def flush(self):
        pass

    def stats(self, serializable=False) -> dict:
        """provide stats in a dictionary format."""
        return self.data


class DigiPiStatsThread(APRSDThread):
    """Thread to log digipi stats."""

    def __init__(self):
        super().__init__("DigiPiStatsLog")
        self._last_total_rx = 0

    def loop(self):
        if self.loop_count % 10 == 0:
            # log the stats every 10 seconds
            stats_json = collector.Collector().collect()
            stats = stats_json["DigipiStats"]
            total_rx = stats["rx"]
            rx_delta = total_rx - self._last_total_rx
            rate = rx_delta / 10

            # Log summary stats
            LOGU.opt(colors=True).info(
                f"<green>RX Rate: {rate} pps</green>  "
                f"<yellow>Total RX: {total_rx}</yellow> "
                f"<red>RX Last 10 secs: {rx_delta}</red>",
            )
            self._last_total_rx = total_rx

        time.sleep(1)
        return True


class DigipiFilterPlugin(plugin.APRSDPluginBase):

    def setup(self):
        """Allows the plugin to do some 'setup' type checks in here.

        If the setup checks fail, set the self.enabled = False.  This
        will prevent the plugin from being called when packets are
        received."""
        # Do some checks here?
        self.enabled = True
        LOG.info(f"{self.__class__.__name__}: {self}")
        collector.Collector().register_producer(DigipiStats)
        packet_collector.PacketCollector().register(DigipiStats)

    def create_threads(self):
        """Create a list of threads to run in the APRS thread pool."""
        return [DigiPiStatsThread()]

    @plugin.hookimpl
    def filter(self, packet: type[packets.Packet]) -> str | packets.MessagePacket:
        """We only want to see packets of type GPSPacket."""
        if self.enabled:
            self.rx_inc()
            if isinstance(packet, packets.GPSPacket):
                return self.process(packet)

    def process(self, packet: packets.core.Packet):
        """We have to implement this method as described in base class."""
        comment = packet.comment
        if comment and 'digipi' in comment.lower():
            packet_log.log(packet)
        return packets.NULL_MESSAGE
