# Copyright (C) 2013 by Aivars Kalvans <aivars.kalvans@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import re
import random
import base64
import logging

from main.models import Proxy


class RandomProxy(object):
    def __init__(self, settings):
        self.proxies = Proxy.objects.filter(status__gt=0)\
            .values_list('address', flat=True)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # Don't overwrite with a random one (server-side state for IP)
        if spider.name == 'pl_usa':
            return
        # if 'proxy' in request.meta:
        #     return
        if not len(self.proxies):
            return

        proxy = random.choice(self.proxies)
        request.meta['proxy'] = proxy
        logging.debug("ASSIGNED PROXY %s" % proxy)
        # if proxy_user_pass:
        #     basic_auth = 'Basic ' + base64.encodestring(proxy_user_pass)
        #     request.headers['Proxy-Authorization'] = basic_auth

    def process_exception(self, request, exception, spider):
        if spider.name == 'pl_usa':
            return
        proxy_address = request.meta['proxy']
        # print 'EXCEPTION: %s' % proxy
        logging.warning('Removing failed proxy <%s>, %d proxies left' %
                        (proxy_address, len(self.proxies)))
        try:
            self.proxies.remove(proxy_address)
            p = Proxy.objects.get(address=proxy_address)
            p.status = -1
            p.save()
        except ValueError:
            pass
