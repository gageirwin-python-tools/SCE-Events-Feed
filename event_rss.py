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
    webhook.edit(name="Steam Card Exchange Events RSS")
    rss_url = "https://www.steamcardexchange.net/include/rss/events.xml"

    response = requests.get(rss_url)

    if not response.ok:
        embed = Embed(
            title="Error Getting Steam Events RSS",
            url=rss_url,
            description=f"{response.status_code} {response.reason}",
            color=RED,
            timestamp=datetime.now(),
        )
        webhook.send(embed=embed)
        quit()

    root = ElementTree.fromstring(response.text)
    namespace = {"media": "http://search.yahoo.com/mrss/"}

    for item in reversed(list(root.iter("item"))):
        title = item.find("title").text
        link = item.find("link").text
        appid = link[59:]
        date = item.find("pubDate").text
        banner_url = item.find("media:content", namespace).attrib["url"]

        if title in past_events:
            continue

        embed = Embed(
            title=title,
            color=GREEN,
            timestamp=datetime.now(),
        )
        embed.add_field(
            name="Release Date:",
            value=date,
            inline=False,
        )
        embed.add_field(
            name="Links:",
            value=f"[**Steam Store**](https://store.steampowered.com/app/{appid})\n[**Game Hub**](https://steamcommunity.com/app/{appid})\n[**Point Shop**](https://store.steampowered.com/points/shop/app/{appid})\n[**Steam Market**](https://steamcommunity.com/market/search?appid=753&category_753_Game%5B%5D=tag_app_{appid})\n[**Steam Card Exchange**]({link})",
            inline=False,
        )
        embed.set_thumbnail(url=banner_url)
        embed.set_image(url=banner_url)
        webhook.send(embed=embed)

        with open(ARCHIVE_FILE, "a") as f:
            f.write(f"{title}\n")


if __name__ == "__main__":
    main()
