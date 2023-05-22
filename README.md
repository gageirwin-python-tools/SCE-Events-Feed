# SCE Events RSS Discord Webhook
 A Python application that processes steamcardexchange.net events RSS feed and sends notifications using Discord webhooks.

## Usage
Install requirements
```bash
pip install -r requirements.txt
```
Run application
```bash
python event_rss.py "YOUR DISCORD WEBHOOK URL"
```
## Note
- On the initial run it will send webhook messages for the last 15 events. These events will then be recorded in `events.txt` and won't be send again.  
- To have the application periodically run set up cron on linux or task scheduler on windows.