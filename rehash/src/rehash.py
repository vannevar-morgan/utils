#! /usr/bin/env python3.4

import sys
import os
import random
import png
import piexif


def make_rtext():
    """
    Return a random string
    """
    return "{0:06d}".format(random.randint(0,999999))


def rehash_png(png_filename):
    """
    Write a tEXt chunk in the png file to change the file hash
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
    Write ExifIFD.UserComment in jpg exif to change the file hash    
    """
    exif_IFD = {piexif.ExifIFD.UserComment: str.encode("\0\0\0\0\0\0\0\0" + REHASH + COMMENT_SEP + make_rtext())}
    # exif_IFD = {piexif.ImageIFD.ImageDescription: "abcdefghijklmnopqrstuvwxyz0123456789"}
    exif_dict = {"Exif":exif_IFD}
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, jpg_filename)


def check_gif_vs_support(gif_filename):
    """
    Confirm gif file version is "GIF89a" so comment blocks are supported
    """
    with open(gif_filename, "rb") as in_file:
        if in_file.read(GIF_HEADER_BYTES) != b"GIF89a":
            return False
        else:
            return True


def get_cblock_offset(gif_filename):
    """
    Return the offset to the first position where writing a comment block is valid.
    This is immediately after the Global Color Table, if present.
    """
    offset = GIF_HEADER_BYTES + GIF_LSD_BYTES # Header bytes (6) + Logical Screen Descriptor (7)
    with open(gif_filename, "rb") as gif_file:
        gif_file.seek(GIF_PF_OFFSET)
        packed_field = gif_file.read(1)
        pf_int = int.from_bytes(packed_field, byteorder="big")
        if(pf_int >> 7 == 1):
            # Global Color Table exists, increase offset by the size of the GCT
            mask = ~(((1 << 5) - 1) << 3) # mask to extract GCT size
            gct_bytes = 3 * 2**((pf_int & mask) + 1)
            assert(gct_bytes >= 6 and gct_bytes <= 768) # min gct size, max gct size
            offset += gct_bytes
    return offset


def insert_gif_comment(gif_filename):
    """
    Insert comment block in the specified gif file
    """
    if not check_gif_vs_support(gif_filename):
        print(MESSAGE_GIF_VERSION_ERROR)
        return
    else:
        comment = REHASH + COMMENT_SEP + make_rtext()
        with open(gif_filename, "r+b") as gif_file:
            comment_offset = get_cblock_offset(gif_filename)
            gif_file.seek(comment_offset)
            data = gif_file.read()
            # insert comment block
            gif_file.write(b"0x21") # extension introducer
            gif_file.write(b"0xfe") # comment label
            gif_file.write(str.encode(chr(len(comment)))) # data size
            gif_file.write(str.encode(comment)) # comment data
            gif_file.write(b"\x00") # block terminator
            # write remaining image data
            gif_file.write(data)
            gif_file.truncate()


def rehash_gif(gif_filename):
    """
    Rehash specified gif file
    """
    try:
        insert_gif_comment(gif_filename)
    except:
        print(MESSAGE_GIF_INSERT_ERROR)
        return


def rehash_mp4(mp4_filename):
    """
    Mutate the meta data in a .mp4 file to change the file hash    
    """
    print("rehash_mp4()")


def rehash_webm(webm_filename):
    """
    Mutate the meta data in a .webm file to change the file hash    
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
MESSAGE_GIF_VERSION_ERROR = "gif version is not supported (gif version must be \"GIF89a\" to support comment blocks)... try updating gif file version?"
MESSAGE_GIF_INSERT_ERROR = "error occurred while inserting comment block in gif file"
MESSAGE_GENERAL_UNKNOWN = "unknown error occurred :("

GIF_HEADER_BYTES = 6
GIF_LSD_BYTES = 7 # 7 bytes, logical screen descriptor
GIF_PF_OFFSET = 10 # offset bytes to the packed field byte, 6 byte header + 4 bytes (logical screen width & height)

if len(sys.argv) != 2:
    print(MESSAGE_USAGE)
    sys.exit(1)

target = sys.argv[1]
if not os.path.isfile(target):
    print(target + SPACE + MESSAGE_NO_FILE)
    sys.exit(1)

# get the target file extension and compare to supported extensions
FILETYPES = ("png", "jpg", "jpeg", "gif")

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
