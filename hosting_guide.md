# Hosting Guide

This is a short hosting guide to help you host Realm Tunes on your own server! Please star this repo if you found it useful!

## Guide Assumptions:

- This guide assumes hosting on Linux or Macos (although it will also work on Windows but some steps may be a little bit different)
- This guide assumes user has knowledge navigating around the terminal
- This guide assumes the user has a discord developer application setup and a bot key ready.

Feel free to reach out to me (`ryebot` on Discord) if you are having trouble with the setup.

## Steps:

1. Clone this repo onto your local computer with the command :
   `git clone https://github.com/Ryanmaxin/Realm-Tunes-2.0.git`

2. Go to the [official lavalink repository](https://github.com/lavalink-devs/Lavalink/releases) and download the latest lavalink server. To do this simply download the most recent `Lavalink.jar` file.

4. Create an `application.yml` file in the cloned repo for the Lavalink server (this server will be what streams music to the bot so that it can play songs). Since this file contains sensitive info, I can't share my exact file. You can find an example file [here](https://github.com/lavalink-devs/Lavalink/blob/master/LavalinkServer/application.yml.example). Depending on your use case you will probably need to add some plugins as well. Here are the ones I use:  
   
   ```
   lavalink:
     plugins:
       - dependency: "com.github.topi314.lavasrc:lavasrc-plugin:4.3.0"
         snapshot: false
       - dependency: "dev.lavalink.youtube:youtube-plugin:1.11.3"
         snapshot: false
       - dependency: "com.github.topi314.lavasearch:lavasearch-plugin:1.0.0"
   ```

   These will probably be out of date when you see this guide, so make sure to grab the latest versions from the following associated GitHubs:  
   - [lavasrc](https://github.com/topi314/LavaSrc)  
   - [youtube-source](https://github.com/lavalink-devs/youtube-source)  
   - [lavasearch](https://github.com/topi314/LavaSearch)  

   **IMPORTANT:** DO NOT ADD MAIN ACCOUNT CREDENTIALS TO THIS FILE, USE A BURNER ACCOUNT AS IT MAY GET BANNED.

4. Create a `.env` file in the cloned repo for private information. By default you will need the following 3 keys populated for Realm Tunes to work:

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

6. Navigate to `/etc/systemd/system` and create two files `realmtunes.service` and `lavalink.service` (This is UNIX, you will need to find an equivalent if you are using Windows). You can use the following two files as templates, but make sure to replace the items in {} appropriately:

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

8. Run the command `./startup.sh`

That's all! That bot should be running and used for playing music on Discord now!

## Additional Notes:

- You can shutdown the bot and server with `./shutdown.sh`.
- You can view the logs for Realm Tunes or Lavalink with `./rt_journal` and `./ll_journal`, respectively. This only shows the most recent 50 lines by default, you can view more by changing the value X in the scripts like:
  - ll_journal: `journalctl -u lavalink.service -n X`
  - rt_journal: `journalctl -u realmtunes.service -n X`
 

## Troubleshooting:

If the bot has suddenly stopped working, there are several steps you can take (in order):

1. **Restart Realm Tunes bot and the Lavalink Server.** You can use `shutdown.sh` and `startup.sh` to do this.
2. **Get the latest version of `Lavalink.jar`.** You can find the latest version [here](https://github.com/lavalink-devs/Lavalink/releases). All you need to do is download the file `Lavalink.jar` and replace the existing file in your bot directory.
3. **Update plugins.** Out of date plugins can break the Lavalink server. All you need to do to update them is search for each one online, find the most recent version, and replace the version number in your `application.yml`.
4. **Create a new youtube account.** If you added an account into `application.yml`, it may get banned if Youtube recognizes that it is a streaming bot. In this case you should create a new account and add the new details to `application.yml`. MAKE SURE IT IS A BURNER ACCOUNT THAT YOU DON'T MIND GETTING BANNED 


