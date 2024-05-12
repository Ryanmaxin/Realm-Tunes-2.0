# Realm-Tunes-2.0

**A Discord music bot built with the Discord.py API, providing 24/7 music for over 350 users across 7 servers.**

<img width="745" alt="image" src="https://user-images.githubusercontent.com/90675771/236710016-529802d2-65b4-42ab-b03a-07a6a2686db1.png">

## Tools Used:

Realm Tunes was created using Python and the Discord.py API. On the backend I used Lavalink to retrieve the audio source (https://github.com/freyacodes/Lavalink), and Wavelink (https://wavelink.readthedocs.io/en/latest/index.html) which provides a Lavalink wrapper for Python.

Realm Tunes is hosted 24/7 on a linux server in Winnipeg, Manitoba. This server was setup by me and is running a headless ubunutu distribution
Both the Realm Tunes bot as well as the Lavalink server are run continuously with systemctl.

## Changes from Realm Tunes 1.0

Realm Tunes 1.0 (https://github.com/Ryanmaxin/Realm-Tunes) was my first attempt to create a music bot. Before I knew about Lavalink, I used tools like YoutubeDL and FFMPEG to retrieve and play audio sources. These tools were not meant to stream music in real-time in the way I was implementing them, and as such, they had severe speed and scaling issues. I knew trying to build further upon these tools would be a mistake and that I needed to find a better way to stream audio, which Lavalink came in handy.

Using Lavalink opened up many additional opportunities for Realm Tunes as well. In addition to seamless streaming, Lavalink has volume and seeking built in, allowing me to use these features that otherwise would have been impossible with FFMPEG.

I also changed my programming philosophy when approaching 2.0. Specifically, I took a much heavier object-orientated approach, whereas in 1.0, I was using functional programming, and I believe this change allowed me to better reason about my bot and will make it easier to add new features in the future.

## Reflection

I wrote most of the code for Realm Tunes in December 2022 after I had finished my fall coop term and before I got busy with school in my upcoming academic term. I couldn't fully finish here, so I spent much of the Winter reading week, plus occasional weekends here and there, finalizing the bot.

Looking back, I'm glad I spent a lot more time planning out the program's layout as it paid for itself many times over in time saved while debugging or adding new features. 

Realm Tunes 2.0 is my first personal project which I have taken the effort to host continuously, which has proven to be a lot more difficult then I expected, but I'm happy to have gotten this experience. 

I have been continually updating Realm Tunes, usually every few months to keep up with changes in Discord.py, LavaLink or Wavelink, and to add requested features.

## Current Commands:

### Join
Realm Tunes joins your current vc if you are in one.

![ezgif-1-fe35afe619](https://user-images.githubusercontent.com/90675771/236711979-7aa9e080-0b8e-4ca0-9dab-d382e6728187.gif)

### Leave
Realm Tunes leaves his current vc.

![ezgif-3-f44ecd29f8](https://user-images.githubusercontent.com/90675771/236712289-550b24a2-b214-41e9-943c-d003f071183d.gif)

### Play
Realm Tunes will immediately play the query if it is a url/playlist, otherwise it will search for the query on YouTube and create a menu where you can choose a song.

![ezgif-3-1be0763039](https://user-images.githubusercontent.com/90675771/236712228-8e6972ab-c423-45ff-84b7-4a407619e722.gif)


### Play Now
Identical to Play, except the desired song will be play immediately even if there is another song playing.

![ezgif-3-48047e2d1f](https://user-images.githubusercontent.com/90675771/236712483-146967e4-32ad-4911-9c9d-5d703c767fe5.gif)

### Clear
Clears the queue and ends the current song.

![ezgif-1-ca6df1d262](https://user-images.githubusercontent.com/90675771/236713370-42faa191-0582-4daa-8be4-e5368a955351.gif)

### Pause
Switches between pausing and unpausing the music.

![ezgif-3-2ceb0cb54d](https://user-images.githubusercontent.com/90675771/236712245-c0c6e4b7-cb80-44ce-b879-6916d5c8901c.gif)

### Skip
Skips the current song.

![ezgif-1-5ba43919b9](https://user-images.githubusercontent.com/90675771/236713946-1b591f57-79fa-4cbf-912c-4026164b0a61.gif)

### Queue
Shows the current queue. Add a number to select specific page (when more then 10 songs)

![ezgif-1-080315ea65](https://user-images.githubusercontent.com/90675771/236712797-cc44b6d3-ce22-40f3-a9e4-9e6940b6594d.gif)

### Loop
Toggles on or off looping. looping repeats the current song after it ends.

![ezgif-1-c1fcaddde2](https://user-images.githubusercontent.com/90675771/236714006-d0d54e9d-7af2-463a-a583-0b566f4e0ca4.gif)

### Shuffle
Puts the current queue in a random order.

![ezgif-3-575deefa9b](https://user-images.githubusercontent.com/90675771/236713275-ded1f34f-932a-4798-bd1f-36662b5cfdce.gif)

### Seek
Begins playing at the specified number of seconds into the song.

![ezgif-1-c75f71b589](https://user-images.githubusercontent.com/90675771/236712630-567527ae-e1b0-4405-bacc-6369acc275dc.gif)

### Previous
Puts the previously played song into the queue. You can add "now" to the end to play the song now.

![ezgif-1-d78ca274f0](https://user-images.githubusercontent.com/90675771/236712728-e062bea1-0ef1-4811-b75a-40d2f0bb6c8d.gif)

### Repeat
Toggles on or off repeating the current queue

![ezgif-1-3a857e9995](https://user-images.githubusercontent.com/90675771/236714094-ef72c7e6-273b-4776-9f3e-76780c8a3ea3.gif)

### Volume
Sets the volume of Realm Tunes to the specified amount

![ezgif-1-8f439a4919](https://user-images.githubusercontent.com/90675771/236714403-7e33957b-5662-4772-b14d-f9d90b833046.gif)

### Current
Shows the song that is currently playing

![ezgif-1-e7b0d53bcd](https://user-images.githubusercontent.com/90675771/236713216-18071f4d-c17c-45a9-bfe1-ef4191463307.gif)

### Restart
Begins playing the current song from the beginning

![ezgif-1-3b0c13ce69](https://user-images.githubusercontent.com/90675771/236713872-6b9a4ef2-859a-4ca5-9165-4cfdfda27d6d.gif)
