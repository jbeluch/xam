import os
import sys
import logging
from cliff.app import App
from cliff.commandmanager import CommandManager


class XAM(App):

    log = logging.getLogger(__name__)

    #CONSOLE_MESSAGE_FORMAT = App.LOG_FILE_MESSAGE_FORMAT

    def __init__(self):
        super(XAM, self).__init__(
            description='XBMC Addon Manager',
            version='0.1',
            command_manager=CommandManager('xam'),
            )

    def initialize_app(self, argv):
        self.log.debug('initialize_app')

        # Set up .xam_cache folder
        try:
            os.mkdir(os.path.join(os.getenv('HOME'), '.xam_cache'))
        except OSError:
            pass

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    myapp = XAM()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
