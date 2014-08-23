import logging
import logging.config
import argparse
import pkg_resources

import yaml
import config


class ModifiedConfig(config.Config):
    def getByPath(self, path, default=None):
        try:
            return config.Config.getByPath(self, path)
        except config.ConfigError:
            return default


def parse_config_options(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--logconfig', '-l', type=argparse.FileType('r'), default=None, help='a logging configuration in YAML format, see https://docs.python.org/2/howto/logging-cookbook.html#logging-cookbook')
    parser.add_argument('--config', '-c', type=argparse.FileType('r'), help='the application configuration, provided by the config module')
    return parser.parse_args(argv)


def get_config(opts):
    c = ModifiedConfig()
    c.load(opts.config)
    return c


def load_log_config(opts):
    if opts.logconfig is None:
        fh = pkg_resources.resource_stream(__name__, 'conf/logging.yaml')
    else:
        fh = opts.logconfig

    logyaml = yaml.load(fh)

    logging.config.dictConfig(logyaml)
