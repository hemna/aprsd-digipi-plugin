from oslo_config import cfg

from aprsd_digipi_plugin.conf import main


CONF = cfg.CONF
main.register_opts(CONF)