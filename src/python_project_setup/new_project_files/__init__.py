# Standard Library
import logging
import logging.config
from os.path import expanduser

# setup loggers
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

# get root logger
# the __name__ resolve to "main" since we are at the root of the project.
logger = logging.getLogger(__name__)
# This will get the root logger since no logger in the configuration has
# this name.

home = expanduser("~")
# Load environment variables
# (.env is not on git nor project folder, so copilot will not be able to
# find it)