#! /usr/bin/env python3.4

import sys
import os
import random
import png
import piexif
import binascii


def make_rtext():
    """
    return a random string
    """
    return "{0:06d}".format(random.randint(0,999999))


def rehash_png(png_filename):
    """
    write a tEXt chunk in the .png file to change the file hash
    """
    comment_text = make_rtext()
    reader = png.Reader(target)
    [width, height, pix, metadata] = reader.read()
    writer = png.Writer(**metadata)
    writer.set_text({REHASH:comment_text})
    with open(png_filename, "wb") as out_file:
        # png.Writer(**metadata).write(out_file, pix)
        writer.write(out_file, pix)
    # except:
    #     print(MESSAGE_FILE_READ_ERROR)
    #     sys.exit(1)


def rehash_jpg(jpg_filename):
    """
    mutate the meta data in a .jpg file to change the file hash    
    """
    exif_IFD = {piexif.ExifIFD.UserComment: str.encode(REHASH + COMMENT_SEP + make_rtext())}
    exif_dict = {"Exif":exif_IFD}
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, jpg_filename)
    
    # exif_dict = piexif.load(jpg_filename)
    # comment_text = make_rtext()
    # print("wrote to exif: " + comment_text)
    # exif_dict["USER_COMMENT"] = comment_text
    # exif_bytes = piexif.dump(exif_dict)
    # piexif.insert(exif_bytes, jpg_filename)

    # exif_dict = {REHASH:make_rtext()}
    # exif_bytes = piexif.dump(exif_dict)
    # piexif.insert(exif_bytes, jpg_filename)


def rehash_gif(gif_filename):
    """
    mutate the meta data in a .gif file to change the file hash    
    """
    print("rehash_gif()")


def rehash_mp4(mp4_filename):
    """
    mutate the meta data in a .mp4 file to change the file hash    
    """
    print("rehash_mp4()")


def rehash_webm(webm_filename):
    """
    mutate the meta data in a .webm file to change the file hash    
    """
    print("rehash_webm()")


MESSAGE_USAGE = "usage: rehash FILENAME"
REHASH = "rehash"
COMMENT_SEP = ": "
SPACE = " "
MESSAGE_NO_FILE = "is not a valid file."
MESSAGE_FILE_EXT_UNKNOWN = "couldn't determine the file type... check file extension?"
MESSAGE_FILE_EXT_UNSUPPORTED = "file type is unsupported."
MESSAGE_SUPPORTED_FILETYPES = "Supported file types:\n.png"
MESSAGE_FILE_READ_ERROR = "error reading file."
MESSAGE_FILE_WRITE_ERROR = "error writing file."
MESSAGE_GENERAL_UNKNOWN = "unknown error occurred :("



if len(sys.argv) != 2:
    print(MESSAGE_USAGE)
    sys.exit(1)

target = sys.argv[1]
if not os.path.isfile(target):
    print(target + SPACE + MESSAGE_NO_FILE)
    sys.exit(1)

# get the target file extension and compare to supported extensions
FILETYPES = ("png", "jpg", "jpeg")

ext_split = os.path.splitext(target)
target_ext = ext_split[1]
if (not target_ext) or target_ext == os.path.extsep:
    print(MESSAGE_FILE_EXT_UNKNOWN)
    sys.exit(1)
target_ext = (target_ext[1:]).lower() # remove extension separator, make extension lower
if target_ext not in FILETYPES:
    print(MESSAGE_FILE_EXT_UNSUPPORTED)
    sys.exit(1)

# filetype is known and supported
#print("filetype is: " + target_ext) # change this to logging

if target_ext == "png":
    rehash_png(target)
elif target_ext == "jpg":
    rehash_jpg(target)
elif target_ext == "jpeg":
    rehash_jpg(target)
elif target_ext == "gif":
    rehash_gif(target)
elif target_ext == "mp4":
    rehash_mp4(target)
elif target_ext == "webm":
    rehash_webm(target)
else:
    pass
