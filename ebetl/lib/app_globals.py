# -*- coding: utf-8 -*-

"""The application's Globals object"""

__all__ = ['Globals']
from tgext.asyncjob import start_async_worker
import tgext.asyncjob

class Globals(object):
    """Container for objects available throughout the life of the application.

    One instance of Globals is created during application initialization and
    is available during requests via the 'app_globals' variable.

    """

    def __init__(self):
        """Do nothing, by default."""
        start_async_worker(progress_tacker=tgext.asyncjob.trackers.redisdb.RedisProgressTracker(host='localhost'))
