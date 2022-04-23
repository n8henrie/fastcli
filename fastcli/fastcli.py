"""fastcli.py :: Command line interface to fast.com by Netflix.

Usage:
    python3 -m fastcli
"""

import argparse
import asyncio
import json
from locale import strcoll
import logging
import time
import urllib.parse
import urllib.request

import aiohttp
import typing

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(name)-12s %(lineno)d %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger_name = "{} :: {}".format(__file__, __name__)
logger = logging.getLogger(logger_name)


async def test_download_speed(session: aiohttp.ClientSession, url: str) -> int:
    """Count the amount of data successfully downloaded."""
    print("test_download_speed started")
    print(url)
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


def _find_from(text: str, start: str, until: str) -> str:
    start_find = text.find(start)
    start_length = len(start)
    end_find = text.find(until, start_find + start_length)
    if -1 in (start_find, end_find):
        return ""
    else:
        start_idx = start_find + start_length
        end_idx = end_find
        return text[start_idx:end_idx]


def _get_token() -> str:
    url = "https://fast.com"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as r:
        resp = r.read().decode()
    js = _find_from(resp, '<script src="', '"')

    js_url = url + js
    js_req = urllib.request.Request(js_url)
    with urllib.request.urlopen(js_req) as jr:
        jsresp = jr.read().decode()

    token = _find_from(jsresp, 'token:"', '"')
    return token


def _build_req_url(url_count, token) -> str:
    import urllib.parse
    
    params = {"https": True, "urlCount": url_count, "token": token}
    query_str = urllib.parse.urlencode({k: str(v) for k, v in params.items()})

    api_base = "https://api.fast.com"
    url = "{}/netflix/speedtest/v2?{}".format(api_base, query_str)

    return url


def _get_targets(url_count, token):
        url = _build_req_url(url_count, token)
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as r:
            resp = r.read().decode()
        resp_json = json.loads(resp)

        targets = resp_json["targets"]

        return targets


async def download(
    token: str = "",
    timeout: typing.Union[float, int] = 10.0,
    https: bool = True,
    url_count: int = 3,
    verbosity: int = logging.WARNING,
) -> float:
    """Create coroutines for speedtest and return results."""
    token = token or _get_token()

    targets = _get_targets(url_count, token)

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        coros = [
            test_download_speed(session, target["url"])
            for target in targets
        ]
        done, pending = await asyncio.wait(coros, timeout=timeout)
        for task in pending:
            task.cancel()
            await task

    duration = time.time() - start_time
    logger.info("Run time: {:.2f} seconds".format(duration))

    results = [task.result() for task in done | pending]
    mb = sum(results) * 8 / 1024 / 1024
    return mb / duration


def run(*, timeout: float = 30, verbosity: int = logging.WARNING) -> float:
    """Create eventloop and run main coroutine."""
    logging.info("Starting fastcli download speed test...")
    loop = asyncio.new_event_loop()
    download_speed = loop.run_until_complete(download(timeout=timeout, verbosity=verbosity))
    loop.close()
    return download_speed


def cli() -> None:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="fastcli", argument_default=argparse.SUPPRESS
    )
    parser.add_argument(
        "--timeout",
        default=30,
        type=float,
        help="Duration of time to run speed test",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=0,
        action="count",
        help="increase verbosity (may repeat up to -vvv)",
    )
    namespace = parser.parse_args()
    args = {k: v for k, v in vars(namespace).items() if v}
    download_speed = run(**args)
    print("Approximate download speed: {:.2f} Mbps".format(download_speed))


if __name__ == "__main__":
    cli()
