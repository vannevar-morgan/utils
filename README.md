Privacy Tools
=============================================

md.py
-------------------
md.py is a media downloader for youtube, dailymotion, vevo, and clipfish that automates downloads using convert2mp3.net

NOTE:
You may wish to consider using something like mps-youtube.  I wrote this script just for fun, it's not meant as a replacement.  I put it under privacy_tools because using this script you don't directly touch google ip's.  The download service still sees everything you download.  You still need to know the URL to the video.  Ideally you might consider setting up mps-youtube on a cheap vps to act as a proxy.  Most likely these kinds of download sites are doing something similar.  I expect this script to break eventually, upon any site changes.


Usage:
>./md.py youtube_url (format)

(format is .flac by default)

Known Issues:

>Videos longer than 90 minutes cannot be converted (but can still be downloaded as an MP4, M4A, or AAC file).  This is a limitation of the convert service, convert2mp3.net.  For videos longer than 90 minutes you can download by specifying either MP4, M4A, or AAC as the file format.

>Sometimes the script will fail while downloading a file (you can rerun the script to try re-downloading).

>Note that for vevo links, you must use the share link as the url for the video to download.  Otherwise the converter service can't find the video.


Repository Contents
-------------------
* **md.py** - Media Downloader for youtube, dailymotion, vevo, and clipfish
* **ofsme** - Obfuscate Me, a tool to obfuscate your text from stylometric analysis and author attribution tools


License Information
-------------------

All code is released under [GNU GPLv3.0](http://www.gnu.org/copyleft/gpl.html).

If you find any errors please message about them.
