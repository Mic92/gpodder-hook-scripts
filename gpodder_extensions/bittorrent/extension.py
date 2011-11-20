#-*- coding: utf-8 -*-
# Automatically open .torrent files with a BitTorrent client
# Copy this script to ~/.config/gpodder/extensions/ to enable it.
# Thomas Perl <thp@gpodder.org>; 2010-10-11
import shlex
import subprocess

from gpodder.extensions import ExtensionParent

DEFAULT_PARAMS = {
    "bittorrent_cmd": {
        "desc": u"Defines the command line bittorrent program:",
        "value": u"transmission-cli %s",
        "type": u"textitem",
    }
}


class gPodderExtensions(ExtensionParent):
    def __init__(self, params=DEFAULT_PARAMS, **kwargs):
        super(gPodderExtensions, self).__init__(params=params, **kwargs)

        self.test = kwargs.get('test', False)
        self.bittorrent_cmd = self.params['bittorrent_cmd']['value']
        self.check_command(self.bittorrent_cmd)

        if self.test:
            self.bittorrent_cmd = 'echo "%s"' % self.bittorrent_cmd

    def on_episode_downloaded(self, episode):
        if episode.extension() == '.torrent':
            self.notify_action("Downloading", episode)
            cmd = self.bittorrent_cmd % episode.local_filename(False)
            
            # Prior to Python 2.7.3, this module (shlex) did not support Unicode input.
            if isinstance(cmd, unicode):
                cmd = cmd.encode('ascii', 'ignore')

            # for testing purpose it's possible to get to stdout+stderr output
            p = subprocess.Popen(shlex.split(cmd), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()

            if p.returncode == 0:
                self.notify_action("Downloading finished", episode)
            else:
                self.notify_action("Downloading finished with erros", episode)
            
            if self.test:                
                return (stdout, stderr)
