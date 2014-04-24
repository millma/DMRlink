#!/usr/bin/env python
#
# Copyright (c) 2013 Cortney T. Buffington, N0MJS and the K0USY Group. n0mjs@me.com
#
# This work is licensed under the Creative Commons Attribution-ShareAlike
# 3.0 Unported License.To view a copy of this license, visit
# http://creativecommons.org/licenses/by-sa/3.0/ or send a letter to
# Creative Commons, 444 Castro Street, Suite 900, Mountain View,
# California, 94041, USA.

# This is a sample application that "records" and replays transmissions for testing.

# THIS MODULE DOES NOT YET WORK!!!!!

from __future__ import print_function
from twisted.internet import reactor
from binascii import b2a_hex as h

import time
from dmrlink import IPSC, UnauthIPSC, NETWORK, networks, logger, dmr_nat, int_id, send_to_ipsc

__author__ = 'Cortney T. Buffington, N0MJS'
__copyright__ = 'Copyright (c) 2014 Cortney T. Buffington, N0MJS and the K0USY Group'
__credits__ = 'Adam Fast, KC0YLK; Dave K; and he who wishes not to be named'
__license__ = 'Creative Commons Attribution-ShareAlike 3.0 Unported'
__version__ = '0.1a'
__maintainer__ = 'Cort Buffington, N0MJS'
__email__ = 'n0mjs@me.com'
__status__ = 'pre-alpha'

class playbackIPSC(IPSC):
    
    def __init__(self, *args, **kwargs):
        IPSC.__init__(self, *args, **kwargs)
        self.CALL_DATA = []
        
    #************************************************
    #     CALLBACK FUNCTIONS FOR USER PACKET TYPES
    #************************************************
    
    def group_voice(self, _network, _src_sub, _dst_sub, _ts, _end, _peerid, _data):
        #_log = logger.debug
        if not _end:
            _tmp_data = _data
            #_tmp_data = dmr_nat(_data, _src_sub, NETWORK[_network]['LOCAL']['RADIO_ID'])
            self.CALL_DATA.append(_tmp_data)
        if _end:
            self.CALL_DATA.append(_data)
            time.sleep(2)
            print()
            print('Repeating Group Voice Call ', h(_src_sub), ' ', h(_dst_sub) ,' ', h(_peerid), ' ', h(NETWORK[_network]['LOCAL']['RADIO_ID']))
            for i in self.CALL_DATA:
                _tmp_data = self.hashed_packet(NETWORK[_network]['LOCAL']['AUTH_KEY'], i)
                # Send the packet to all peers in the target IPSC
                send_to_ipsc(_network, _tmp_data)
                print(_network, ' ', h(_tmp_data))
                time.sleep(0.05)
            self.CALL_DATA = []
        

class playbackUnauthIPSC(playbackIPSC):
    
    # There isn't a hash to build, so just return the data
    #
    def hashed_packet(self, _key, _data):
        return _data   
    
    # Remove the hash from a packet and return the payload... except don't
    #
    def strip_hash(self, _data):
        return _data
    
    # Everything is validated, so just return True
    #
    def validate_auth(self, _key, _data):
        return True
        
if __name__ == '__main__':
    logger.info('DMRlink \'playback.py\' (c) 2014 N0MJS & the K0USY Group - SYSTEM STARTING...')
    for ipsc_network in NETWORK:
        if NETWORK[ipsc_network]['LOCAL']['ENABLED']:
            if NETWORK[ipsc_network]['LOCAL']['AUTH_ENABLED']:
                networks[ipsc_network] = playbackIPSC(ipsc_network)
            else:
                networks[ipsc_network] = playbackUnauthIPSC(ipsc_network)
            reactor.listenUDP(NETWORK[ipsc_network]['LOCAL']['PORT'], networks[ipsc_network])
    reactor.run()