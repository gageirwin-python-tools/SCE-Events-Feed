import argparse
import os
import time
from datetime import datetime, timedelta
from xml.etree import ElementTree

import requests
from discord import Embed, SyncWebhook

ARCHIVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.txt")

RED = 0xFF0000
GREEN = 0x00FF00


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--indefinitely",
        action="store_true",
        help="Indefinitely run the application and check www.steamcardexchange.net Event Feed one minute after it is updated. (Feed updates every hour on the hour)",
    )
    parser.add_argument("webhook_url", type=str, help="Discord Webhook")
    return parser.parse_args()


def main():
    args = parse_arguments()
    webhook_username = "SCE Event Feed"
    sce_favicon = "https://www.steamcardexchange.net/favicon-256x256.png"

    while True:
        past_events = []
        if os.path.exists(ARCHIVE_FILE):
            with open(ARCHIVE_FILE, "r") as f:
                past_events = f.read().splitlines()

        webhook = SyncWebhook.from_url(args.webhook_url)
        rss_url = "https://www.steamcardexchange.net/include/rss/events.xml"

        response = requests.get(rss_url)

        if not response.ok:
            embed_dict = {
                "author": {
                    "name": webhook_username,
                    "url": rss_url,
                    "icon_url": sce_favicon,
                },
                "title": f"Error: {response.status_code} | {response.reason}",
                "color": RED,
            }
            webhook.send(
                username=webhook_username,
                avatar_url=sce_favicon,
                embed=Embed.from_dict(embed_dict),
            )
            quit()

        root = ElementTree.fromstring(response.text)
        channel = root.find("channel")
        feed_title = channel.find("title").text
        feed_link = channel.find("link").text
        feed_date = channel.find("pubDate").text

        for item in reversed(list(channel.findall("item"))):
            title = item.find("title").text
            link = item.find("link").text
            appid = link[59:]
            banner_url = item.find(
                "media:content", {"media": "http://search.yahoo.com/mrss/"}
            ).attrib["url"]

            if title in past_events:
                continue

            embed_dict = {
                "author": {
                    "name": feed_title,
                    "url": feed_link,
                    "icon_url": sce_favicon,
                },
                "title": title,
                "url": link,
                "color": GREEN,
                "fields": [
                    {
                        "name": "Release Date:",
                        "value": item.find("pubDate").text,
                        "inline": False,
                    },
                    {
                        "name": "Links:",
                        "value": f"[**Steam Store**](https://store.steampowered.com/app/{appid})\n[**Game Hub**](https://steamcommunity.com/app/{appid})\n[**Point Shop**](https://store.steampowered.com/points/shop/app/{appid})\n[**Steam Market**](https://steamcommunity.com/market/search?appid=753&category_753_Game%5B%5D=tag_app_{appid})",
                        "inline": False,
                    },
                ],
                "thumbnail": {"url": banner_url},
                "image": {"url": banner_url},
                "timestamp": datetime.strptime(
                    feed_date, "%a, %d %b %Y %H:%M:%S %Z"
                ).isoformat(),
            }

            webhook.send(
                username=webhook_username,
                avatar_url=sce_favicon,
                embed=Embed.from_dict(embed_dict),
            )

            with open(ARCHIVE_FILE, "a") as f:
                f.write(f"{title}\n")

        if args.indefinitely == False:
            break

        last_updated = datetime.strptime(feed_date, "%a, %d %b %Y %H:%M:%S %Z")
        next_update = last_updated + timedelta(hours=1, minutes=1)
        dt = (next_update - datetime.utcnow()).total_seconds()
        sleep = dt if dt > 0 else 0
        print(f"Waiting for next update in {sleep} seconds.")
        time.sleep(sleep)


if __name__ == "__main__":
    main()
