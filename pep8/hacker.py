#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

try:
    import urllib.parse as urlparse   # py3
except ImportError:
    import urlparse
from grab import Grab
import aiohttp
import asyncio
import async_timeout


class Hacker(object):
    base = 'http://localhost:5000'
    url = 'check_pep8'
    code = 'pocet=45'
    active = [135, 188, 147, 153, 229, 221, 241, 243, 235, 251, 230]
    active = [235, 249]
    active = [('192.168.174.%s' % i4) for i4 in active]
    active2 = ['192.168.174.251', '192.168.174.135', '192.168.174.248',
              ]

    def __init__(self):
        self.g = Grab()

    def go(self, base=None, url=None, code=None):
        base = base or self.base
        url = url or self.url
        code = code or self.code

        url = urlparse.urljoin(base, url)
        self.g.go(url)        # except grab.error.GrabTimeoutError
        gff = self.g.doc.form_fields()
        gff['code'] = code
        self.g.go(url, post=gff)
        bd = self.g.doc.tree.cssselect('body')[0]
        return bd.text_content()

    def go2(self, base=None, url=None, code=None):
        base = base or self.base
        url = url or self.url
        code = code or self.code

        url = urlparse.urljoin(base, url)
        self.g.go(url)        # except grab.error.GrabTimeoutError
        bd = self.g.doc.tree.cssselect('body')[0]
        return bd.text_content()

    def attack1(self):
        for ip in self.active:
            try:
                res = self.go2(base='http://%s:5000/check_pep8' % ip)
                print(ip, res[:120].replace('\n', ' '))
            except Exception as exc:
                print(ip, '---')

    async def fetch(self, session, url):
        with async_timeout.timeout(10):
            async with session.get(url) as response:
                return await response.text()

    async def attack_main(self, loop):
        async with aiohttp.ClientSession(loop=loop) as session:
            for i in range(100000):
                print(i)
                for ip in self.active:
                    try:
                        html = await self.fetch(session, 'http://%s:5000/check_pep8' % ip)
                    except Exception:
                        html = '*****'
                    print(i, ip, html[:100].replace('\n', ' '))

    def attack2(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.attack_main(loop))

    def attackX(self):
        import asyncio
        loop = asyncio.get_event_loop()
        for i in range(1000):
            print(i)
            for ip in self.active2:
                loop.run_until_complete(self.ping(loop, ip))
        loop.close()

    async def ping(self, loop, ip):
        #from concurrent.futures import ThreadPoolExecutor
        #try:
        #executor = ThreadPoolExecutor()
        await urllib.request.urlopen(get('http://%s:5000/check_pep8' % ip)).read()
        #result = await loop.run_in_executor(executor, self.go(base='http://%s:5000/check_pep8' % ip))
        #result = await self.go(base='http://%s:5000/check_pep8' % ip)
        print(ip, result[:150])
        #except Exception as exc:
        #    print(ip, '---')


if __name__ == '__main__':
    hacker = Hacker()
    hacker.attack2()
    #hacker.go()
