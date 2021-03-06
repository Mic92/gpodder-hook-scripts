#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import urllib
import unittest

from mock import patch

import logging
FMT = '%(created)f [%(name)s] %(levelname)s: %(message)s'
logging.basicConfig(format=FMT, level=logging.CRITICAL)
logging.basicConfig()

from config import data

test_dir = os.path.dirname(os.path.abspath(__file__))
extension_dir = os.path.join(os.path.split(test_dir)[0], 'gpodder_extensions')

def read_args():
    #read command line arguments
    parser = argparse.ArgumentParser(description='start gPodder extension script tests')
    parser.add_argument('--gpo', required=True, dest='gpo',
                        help='Path of the gPodder')
    return parser.parse_args()


def append_python_path(gpo_path, extension):
    gpo_src_path = os.path.join(gpo_path, 'src')
    if os.path.exists(gpo_src_path):
        sys.path.append(gpo_src_path)

    if os.path.exists(extension):
        sys.path.append(extension)


def my_retrieve_resume(self, url, filename, reporthook=None, data=None):
    fp = urllib.urlopen(url)
    return fp.info(), fp.geturl()


def ins_test_podcast(core, conf):
    from gpodder import download

    with patch.object(download.DownloadURLOpener, 'retrieve_resume', my_retrieve_resume):
        podcast = core.model.load_podcast(conf['url'], create=True)

        if not podcast.pause_subscription:
            podcast.pause_subscription = True
            podcast.save()

        episode2dl = conf['episode']
        if episode2dl is not None and 'mediafile' in conf:
            episode = podcast.get_all_episodes()[episode2dl]
            if (not episode.was_downloaded(and_exists=True)):
                task = download.DownloadTask(episode, core.config)
                task.status = download.DownloadTask.QUEUED
                task.run()
                shutil.copyfile(conf['mediafile'], episode.local_filename(create=False))


def init_data(gpo_dir):
    from gpodder import core

    shutil.rmtree(gpo_dir, ignore_errors=True)

    os.environ['GPODDER_DISABLE_EXTENSIONS'] = 'yes'
    gpo_core = core.Core()

    # set preferred youtube format to FLV (for flv2mp4 test)
    gpo_core.config.youtube_preferred_fmt_id = 34
    gpo_core.config.save()

    for name, conf in data.TEST_PODCASTS.items():
        ins_test_podcast(gpo_core, conf)

    gpo_core.shutdown()
    os.environ['GPODDER_DISABLE_EXTENSIONS'] = ''


if __name__ == "__main__":
    args = read_args()
    append_python_path(args.gpo, extension_dir)

    test_dir = os.path.dirname(__file__)
    gpo_dir = os.path.join(test_dir, 'gpodder3')
    os.environ['GPODDER_HOME'] = os.path.join(gpo_dir, 'config')
    os.environ['GPODDER_DOWNLOAD_DIR'] = os.path.join(gpo_dir, 'config', 'Downloads')
    os.environ['GPODDER_EXTENSIONS'] = extension_dir

    init_data(gpo_dir)

    #import all test files
    import bittorrent_downloader_test
    import cmml_generator_test
    import mp3gain_test
    import tfh_shownotes_test
    import zpravy_test

    loader = unittest.TestLoader()

    suite = loader.loadTestsFromModule(bittorrent_downloader_test)
    suite.addTests(loader.loadTestsFromModule(cmml_generator_test))
    suite.addTests(loader.loadTestsFromModule(mp3gain_test))
    suite.addTests(loader.loadTestsFromModule(tfh_shownotes_test))
    suite.addTests(loader.loadTestsFromModule(zpravy_test))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
