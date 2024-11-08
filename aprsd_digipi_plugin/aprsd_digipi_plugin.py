import logging

from oslo_config import cfg
from aprsd import packets, plugin, threads, utils
from aprsd.utils import trace

import aprsd_digipi_plugin
from aprsd_digipi_plugin import conf  # noqa

CONF = cfg.CONF
LOG = logging.getLogger("APRSD")


class DigipiFilterPlugin(plugin.APRSDPluginBase):

    enabled = False

    def setup(self):
        """Allows the plugin to do some 'setup' type checks in here.

        If the setup checks fail, set the self.enabled = False.  This
        will prevent the plugin from being called when packets are
        received."""
        # Do some checks here?
        self.enabled = True

    def create_threads(self):
        """This allows you to create and return a custom APRSDThread object.

        Create a child of the aprsd.threads.APRSDThread object and return it
        It will automatically get started.

        You can see an example of one here:
        https://github.com/craigerl/aprsd/blob/master/aprsd/threads.py#L141
        """
        if self.enabled:
            # You can create a background APRSDThread object here
            # Just return it for example:
            # https://github.com/hemna/aprsd-weewx-plugin/blob/master/aprsd_weewx_plugin/aprsd_weewx_plugin.py#L42-L50
            #
            return []

    @trace.trace
    def process(self, packet: packets.core.Packet):

        LOG.info("DigipiFilterPlugin Plugin")

        from_callsign = packet.from_call
        message = packet.message_text

        # Now we can process
        return "some reply message"
