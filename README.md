utils
=============================================

md.py
-------------------
md.py is a media downloader for youtube, dailymotion, vevo, and clipfish that automates downloads using convert2mp3.net

NOTE:
You may wish to consider using something like youtube-dl / mps-youtube.  I wrote this script just for fun, it's not meant as a replacement.  Using this script you don't directly touch google ip's.  The download service still sees everything you download.  You still need to know the URL to the video.  Ideally you might consider setting up youtube-dl / mps-youtube on a cheap vps to act as a proxy.  Most likely these kinds of download sites are doing something similar.  I expect this script to break eventually, upon any site changes.


Usage:
>./md.py youtube_url (format)

(format is .flac by default)

Known Issues:

>Videos longer than 90 minutes cannot be converted (but can still be downloaded as an MP4, M4A, or AAC file).  This is a limitation of the convert service, convert2mp3.net.  For videos longer than 90 minutes you can download by specifying either MP4, M4A, or AAC as the file format.

>Sometimes the script will fail while downloading a file (you can rerun the script to try re-downloading).

>Note that for vevo links, you must use the share link as the url for the video to download.  Otherwise the converter service can't find the video.


8ch_scraper.py
-------------------
8ch_scraper.py is a media downloader for threads on 8ch.net.

Its intended usage is:
>./8ch_scraper thread_url dl_dir=./8ch_media_(op_postnum), force_download=False

>use a new tab in terminal for each thread you're monitoring.

>re-run the script occasionally to download new files posted to the thread.

Known Issues:

>Sometimes a file posted to a thread will be downloaded each time the script is run - even if the file already exists (normally, existing files are skipped).  If the file already exists, the new filename will be appended to with a random number so as not to overwrite the original file, unless the force_download flag is set to True.

>Untested on .pdf files

Use wget when appropriate :)


ofsme
-------------------
This is a text obfuscation tool but it's not finished and I've been working on other things, I'll come back to it eventually.

NOT under active development.


rehash
-------------------
Some sites prevent uploading duplicate files.  Usually this is done by taking the file hash and checking against hashes of files already uploaded.  rehash will add metadata to common media files so they will hash differently.  This will allow uploading duplicate files (unless the site uses other means to detect duplicates e.g., hashing the data not the file, or image analysis).

Under active development.



Repository Contents
-------------------
* **md.py** - Media Downloader for youtube, dailymotion, vevo, and clipfish
* **8ch_scraper.py** - Media downloader for threads on 8ch.net
* **ofsme** - Obfuscate Me, a tool to obfuscate your text from stylometric analysis and author attribution tools
* **rehash** - Need to upload duplicate files??  Change the hash on common media files without changing the content (changes some metadata).


License Information
-------------------

Released under [GNU GPLv3.0](http://www.gnu.org/copyleft/gpl.html).

Please give credit by linking this page.

If you find any errors please message about them.