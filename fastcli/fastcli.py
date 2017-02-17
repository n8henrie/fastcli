"""fastcli.py :: Command line interface to fast.com by Netflix

Usage:
    python3 -m fastcli
"""

import argparse
import asyncio
import json
import logging
import time
import urllib.parse
import urllib.request

import aiohttp
import typing

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s %(name)-12s %(lineno)d %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    )

logger_name = "{} :: {}".format(__file__, __name__)
logger = logging.getLogger(logger_name)


async def test_speed(session: aiohttp.ClientSession, url: str):
    result = 0
    try:
        async with session.get(url) as resp:
            while True:
                chunk = await resp.content.read(56)
                if not chunk:
                    break
                else:
                    result += len(chunk)
    except asyncio.CancelledError:
        pass
    finally:
        return result


def find_from(text: str, start: str, until: str) -> str:
    start_find = text.find(start)
    start_length = len(start)
    end_find = text.find(until, start_find + start_length)
    if -1 in (start_find, end_find):
        return ""
    else:
        return text[start_find + start_length:end_find]


def get_token() -> str:
    url = 'https://fast.com'
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as r:
        resp = r.read().decode()
    js = find_from(resp, '<script src="', '"')

    js_url = url + js
    js_req = urllib.request.Request(js_url)
    with urllib.request.urlopen(js_req) as jr:
        jsresp = jr.read().decode()

    token = find_from(jsresp, 'token:"', '"')
    return token


def main(token: str='', timeout: typing.Union[float, int]=10.0, https:
         bool=True, url_count: int=3):

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    token = token or get_token()
    api_base = 'https://api.fast.com'

    params = {
        'https': True,
        'urlCount': 3,
        'token': token
        }
    query_str = urllib.parse.urlencode({k: str(v) for k, v in params.items()})
    url = api_base + '/netflix/speedtest?' + query_str

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as r:
        resp = r.read().decode()
    resp_json = json.loads(resp)

    start_time = time.time()

    with aiohttp.ClientSession() as session:
        coros = [test_speed(session, url['url'])
                 for url in resp_json]
        fut = asyncio.gather(*coros)
        try:
            loop.run_until_complete(asyncio.wait_for(fut, timeout=timeout))
        except asyncio.TimeoutError:
            loop.run_until_complete(fut)
        finally:
            loop.close()

    duration = time.time() - start_time
    logger.info("Run time: {:.2f} seconds".format(duration))

    mb = sum(fut.result()) * 8 / 1024 / 1024
    return mb / duration


def cli() -> None:
    logging.info("Starting fastcli download speed test...")
    parser = argparse.ArgumentParser(prog='fastcli',
                                     argument_default=argparse.SUPPRESS)
    parser.add_argument('--timeout', default=10, type=float,
                        help="Duration of time to run speed test")
    namespace = parser.parse_args()
    args = {k: v for k, v in vars(namespace).items() if v}

    speed = main(**args)
    print("Approximate download speed: {:.2f} Mbps".format(speed))


if __name__ == "__main__":
    cli()
