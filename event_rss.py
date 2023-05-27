import argparse
import os
from datetime import datetime
from xml.etree import ElementTree

import requests
from discord import Embed, SyncWebhook

ARCHIVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.txt")

RED = 0xFF0000
GREEN = 0x00FF00


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("webhook_url", type=str, help="Discord Webhook")
    args = parser.parse_args()
    return args.webhook_url


def main():
    webhook_url = parse_arguments()
    past_events = []
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, "r") as f:
            past_events = f.read().splitlines()

    webhook = SyncWebhook.from_url(webhook_url)
    rss_url = "https://www.steamcardexchange.net/include/rss/events.xml"

    response = requests.get(rss_url)

    if not response.ok:
        embed_dict = {
            "author": {
                "name": f"Steam Card Exchange Events RSS",
                "url": "https://www.steamcardexchange.net/include/rss/events.xml",
                "icon_url": "https://www.steamcardexchange.net/favicon-256x256.png",
            },
            "title": f"Error: {response.status_code} {response.reason}",
            "url": rss_url,
            "color": RED,
        }
        webhook.send(
            username="SCE RSS",
            avatar_url="https://www.steamcardexchange.net/favicon-256x256.png",
            embed=Embed.from_dict(embed_dict),
        )
        quit()

    root = ElementTree.fromstring(response.text)
    namespace = {"media": "http://search.yahoo.com/mrss/"}

    for item in reversed(list(root.iter("item"))):
        title = item.find("title").text
        link = item.find("link").text
        appid = link[59:]
        banner_url = item.find("media:content", namespace).attrib["url"]

        if title in past_events:
            continue

        fields = []
        fields.append(
            {
                "name": "Release Date:",
                "value": item.find("pubDate").text,
                "inline": False,
            }
        )
        fields.append(
            {
                "name": "Links:",
                "value": f"[**Steam Store**](https://store.steampowered.com/app/{appid})\n[**Game Hub**](https://steamcommunity.com/app/{appid})\n[**Point Shop**](https://store.steampowered.com/points/shop/app/{appid})\n[**Steam Market**](https://steamcommunity.com/market/search?appid=753&category_753_Game%5B%5D=tag_app_{appid})",
                "inline": False,
            }
        )

        embed_dict = {
            "author": {
                "name": f"Steam Card Exchange Events RSS",
                "url": "https://www.steamcardexchange.net/include/rss/events.xml",
                "icon_url": "https://www.steamcardexchange.net/favicon-256x256.png",
            },
            "title": title,
            "url": link,
            "color": GREEN,
            "fields": fields,
            "thumbnail": {"url": banner_url},
            "image": {"url": banner_url},
            "timestamp": datetime.utcnow().isoformat(),
        }

        webhook.send(
            username="SCE RSS",
            avatar_url="https://www.steamcardexchange.net/favicon-256x256.png",
            embed=Embed.from_dict(embed_dict),
        )

        with open(ARCHIVE_FILE, "a") as f:
            f.write(f"{title}\n")


if __name__ == "__main__":
    main()
