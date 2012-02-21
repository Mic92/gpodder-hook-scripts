#!/usr/bin/python
# -*- coding: utf-8 -*-
####
# 2011-03-28 written by Jan Lana <lana.jan@gmail.org>
#
# This script is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# gPodder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# The $subj podcast rss does not contain id and pubdate.
# Because of the missing guid gPodder reports always "no new episodes" for the podcast.
# This extension fix this. The pubdate can be calculated from the audio file url
# and I used the same number as guid.

import re
import time

import logging
logger = logging.getLogger(__name__)


# Metadata for this extension
__title__ = 'Zpravy'
__description__ = 'Insert a missing GUI to podcasts from zpravy'
__author__ = "Jan Lana <lana.jan@gmail.org>, Bernd Schlapsi <brot@gmx.info>"


# settings
domain = u'http://.*/media/zpravy/(\d+)-cro1_(\d\d)_(\d\d)_(\d\d)_(\d\d).mp3'


class gPodderExtension:
    def __init__(self, container):
        self.container = container

    def on_load(self):
        logger.info('Extension "%s" is being loaded.' % __title__)

    def on_unload(self):
        logger.info('Extension "%s" is being unloaded.' % __title__)

    def on_episode_save(self, episode):
        ts = self._get_pubdate(episode)
        if ts is not None:
            episode.published = ts
            episode.guid = int(ts)
            episode.save()
            episode.db.commit()
            logger.info(u'updated pubDate and guid for podcast: (%s/%s)' %
                (episode.channel.title, episode.title))

    def _get_pubdate(self, episode):
        m = re.search(domain, episode.url)
        if m:
            return time.mktime([int(m.group(1)), int(m.group(2)), int(m.group(3)),
                int(m.group(4)), int(m.group(5)), 0, -1, -1, -1])

        return None