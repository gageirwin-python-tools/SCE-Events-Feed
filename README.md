# SCE Events Feed
A Python application that processes [www.steamcardexchange.net](www.steamcardexchange.net) Event Feed and sends a notification using Discord webhooks.

## Usage
Install requirements
```bash
pip install -r requirements.txt
```
Run application
```bash
python event_rss.py [OPTIONS] "YOUR DISCORD WEBHOOK URL"
```
## Options
 - `--indefinitely` : Indefinitely run the application and check www.steamcardexchange.net Event Feed one minute after it is updated. (Feed updates every hour on the hour)
## Note
- On the initial run it will send (15) webhooks for all events in the feed.
- All sent events will be recorded in `events.txt` and won't be sent again.