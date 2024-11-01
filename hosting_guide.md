# Hosting Guide

This is a short hosting guide to help you host Realm Tunes on your own server! Please star this repo if you found it useful!

## Guide Assumptions:

- This guide assumes hosting on Linux or Macos
- This guide assumes user has knowledge navigating around the terminal
- This guide assumes the user has a discord developer application setup and a bot key ready.

## Steps:

1. Clone this repo onto your local computer with the command :
   `git clone https://github.com/Ryanmaxin/Realm-Tunes-2.0.git`

2. Create an `application.yml` file in the cloned repo for the Lavalink server (this server will be what streams music to the bot so that it can play songs). Since this file contains sensitive info, I can't share my exact file. You can find an example file [here](https://github.com/lavalink-devs/Lavalink/blob/master/LavalinkServer/application.yml.example), and you can learn more about the Lavalink server [here](https://github.com/lavalink-devs/Lavalink).

3. Create a `.env` file in the cloned repo for private information. By default you will need the following 3 keys populated for Realm Tunes to work:

```
BOT_KEY={Your bot key here, you need to get this from the Discord Developer Portal}
SERVER_HOST={Your server address here, will be the same as in your application.yml}
SERVER_KEY={Your server password here, will be the same as in your application.yml}
```

4. Install all of the dependencies needed for Realm Tunes. Inside of the cloned repo, you can do this with:

```
python -m venv {/path/to/new/virtual/environment}
source {/path/to/new/virtual/environment}/bin/activate
pip install -r requirements.txt
```

5. Make sure you have [Java](https://www.java.com/en/) installed and updated. This is needed for the Lavalink server.

6. Navigate to `/etc/systemd/system` and create two files `realmtunes.service` and `lavalink.service`. You can use the following two files as templates, but make sure to replace the items in {} appropriately:

```
# realmtunes.service
[Unit]
Description=Runs the Discord.py scripts for Realm Tunes
After=network.target

[Service]
ExecStart={/path/to/venv/python3} {/path/to/main.py}
WorkingDirectory={/path/to/cloned/repo}
Restart=always
User={desired user}
Group={desired group (can be same as user)}

[Install]
WantedBy=default.target
```

```
# lavalink.service
[Unit]
Description=Runs the Lavalink server for Realm Tunes
After=network.target

[Service]
ExecStart={/path/to/java} -jar {/path/to/LavaLink.jar}
WorkingDirectory=/home/rt/Realm-Tunes-2.0
Restart=always
User={desired user}
Group={desired group (can be same as user)}

[Install]
WantedBy=default.target
```

7. Go back to the cloned repo, and enter the folder `service_commands`.

8. Run the command `/startup.sh`

That's all! That bot should be running and used for playing music on Discord now!

## Additional Notes:

- You can shutdown the bot and server with /shutdown.sh
- You can view the logs for Realm Tunes or Lavalink with `/rt_journal` and `/ll_journal`, respectively
