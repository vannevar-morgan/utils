#! /usr/bin/env python3

import sys
import os
import random
import piexif
import argparse
from shutil import copyfile
import binascii


def make_rtext():
    """
    Return a random string
    """
    return "{0:09d}".format(random.randint(0,999999999))


def is_png(png_filename):
    """
    Check if the file begins with the PNG signature.

    Return the offset to the beginning of the IHDR chunk if it's a PNG file.
    (This offset will be PNG_SIG_LEN unless the file is not PNG)

    Return None if the file is not a PNG file.
    """
    PNG_SIG = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a" # png signature
    PNG_SIG_LEN = 8
    try:
        with open(png_filename, "rb") as png_file:
            sig = png_file.read(PNG_SIG_LEN)
            if sig == PNG_SIG:
                return PNG_SIG_LEN
            else:
                return None
    except:
        return None
    

def get_png_ihdr_size(png_filename, ihdr_offset):
    """
    Return the size in bytes of the PNG IHDR chunk.
    """
    CHUNK_FIELD_LEN = 4 # size in bytes for the length, chunk type, & crc fields
    ihdr_size = None
    with open(png_filename, "rb") as png_file:
        png_file.seek(ihdr_offset)
        # read the length field of IHDR chunk, which represents the length of the chunk data field
        ihdr_data_len = png_file.read(CHUNK_FIELD_LEN)
        ihdr_size = (3 * CHUNK_FIELD_LEN) + int.from_bytes(ihdr_data_len, byteorder="big")
    assert(ihdr_size <= (2**31) - 1) # max chunk size
    return ihdr_size


def make_png_text_chunk():
    """
    Return a text chunk to write to a PNG file.
    """
    CHUNK_FIELD_LEN = 4 # size in bytes for the length, chunk type, & crc fields
    comment = "rehash: " + make_rtext()
    CHUNK_TYPE = b"\x74\x45\x58\x74"
    CHUNK_DATA = b"Comment\x00" + str.encode(comment)
    # CHUNK_DATA_LENGTH_UNPADDED = str.encode(chr(len(CHUNK_DATA))) # chunk data length, unpadded (must be 4 bytes, padded)
    # CHUNK_DATA_LENGTH = b"\x00" * (CHUNK_FIELD_LEN - len(CHUNK_DATA_LENGTH_UNPADDED)) + CHUNK_DATA_LENGTH_UNPADDED
    CHUNK_DATA_LENGTH = bytes.fromhex("{0:08x}".format(len(CHUNK_DATA)))
    crc = binascii.crc32(CHUNK_TYPE + CHUNK_DATA) & 0xffffffff
    crc_hex = "{0:08x}".format(crc)
    CHUNK_CRC = bytes.fromhex(crc_hex)
    return CHUNK_DATA_LENGTH + CHUNK_TYPE + CHUNK_DATA + CHUNK_CRC


def rehash_png(png_filename):
    """
    Write a tEXt chunk in the png file to change the file hash
    """
    ihdr_beg = is_png(png_filename)
    if ihdr_beg:
        ihdr_len = get_png_ihdr_size(png_filename, ihdr_beg)
        with open(png_filename, "r+b") as png_file:
            png_file.seek(ihdr_beg + ihdr_len)
            data = png_file.read()
            png_file.seek(ihdr_beg + ihdr_len)
            png_file.write(make_png_text_chunk())
            png_file.write(data)
            png_file.truncate()


# def rehash_png(png_filename):
#     """
#     Write a tEXt chunk in the png file to change the file hash
#     """
#     comment_text = make_rtext()
#     reader = png.Reader(png_filename)
#     [width, height, pix, metadata] = reader.read()
#     writer = png.Writer(**metadata)
#     writer.set_text({"rehash":comment_text})
#     with open(png_filename, "wb") as out_file:
#         # png.Writer(**metadata).write(out_file, pix)
#         writer.write(out_file, pix)


def rehash_jpg(jpg_filename):
    """
    Write ExifIFD.UserComment in jpg exif to change the file hash    
    """
    exif_IFD = {piexif.ExifIFD.UserComment: str.encode("\0\0\0\0\0\0\0\0rehash: " + make_rtext())}
    # exif_IFD = {piexif.ImageIFD.ImageDescription: "abcdefghijklmnopqrstuvwxyz0123456789"}
    exif_dict = {"Exif":exif_IFD}
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, jpg_filename)


def check_gif_vs_support(gif_filename):
    """
    Confirm gif file version is "GIF89a" so comment blocks are supported
    """
    GIF_HEADER_BYTES = 6
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
    GIF_HEADER_BYTES = 6
    GIF_LSD_BYTES = 7 # 7 bytes, logical screen descriptor
    GIF_PF_OFFSET = 10 # offset bytes to the packed field byte, 6 byte header + 4 bytes (logical screen width & height)
    offset = GIF_HEADER_BYTES + GIF_LSD_BYTES # Header bytes + Logical Screen Descriptor
    with open(gif_filename, "rb") as gif_file:
        gif_file.seek(GIF_PF_OFFSET)
        packed_field = gif_file.read(1)
        pf_int = int.from_bytes(packed_field, byteorder="big")
        if(pf_int >> 7 == 1):
            # Global Color Table exists, increase offset by the size of the GCT
            mask = ~(((1 << 5) - 1) << 3) # mask (00000111) to extract GCT size
            gct_bytes = 3 * 2**((pf_int & mask) + 1)
            assert(gct_bytes >= 6 and gct_bytes <= 768) # min gct size, max gct size
            offset += gct_bytes
    return offset


def insert_gif_comment(gif_filename):
    """
    Insert comment block in the specified gif file
    """
    if not check_gif_vs_support(gif_filename):
        MESSAGE_GIF_VERSION_ERROR = "gif version is not supported (gif version must be \"GIF89a\" to support comment blocks)... try updating gif file version?"
        print(MESSAGE_GIF_VERSION_ERROR)
        return
    else:
        comment = "rehash: " + make_rtext()
        with open(gif_filename, "r+b") as gif_file:
            comment_offset = get_cblock_offset(gif_filename)
            gif_file.seek(comment_offset)
            data = gif_file.read()
            # insert comment block
            gif_file.write(b"\x21") # extension introducer
            gif_file.write(b"\xfe") # comment label
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
    MESSAGE_GIF_INSERT_ERROR = "error occurred while inserting comment block in gif file"
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


def rehash_ebml(ebml_filename):
    """
    Write a tag segment at the end of the specified ebml container
    """
    comment = "rehash: " + make_rtext()
    ebml_id_tags = b"\x12\x54\xc3\x67"
    ebml_id_tag = b"\x73\x73"
    ebml_id_targets = b"\x63\xc0"
    ebml_id_simple_tag = b"\x67\xc8"
    ebml_id_tag_name = b"\x45\xa3"
    ebml_id_tag_language = b"\x44\x7a"
    ebml_id_tag_default = b"\x44\x84"
    ebml_id_tag_string = b"\x44\x87"
    tag_name = b"COMMENT"
    tag_language = b"eng"
    tag_segment = (ebml_id_tags
                   + ebml_id_tag
                   + ebml_id_targets
                   + ebml_id_simple_tag
                   + (ebml_id_tag_name + tag_name)
                   + (ebml_id_tag_language + tag_language)
                   + ebml_id_tag_default
                   + (ebml_id_tag_string + str.encode(comment))
    )
    with open(ebml_filename, "ab") as ebml_file:
        ebml_file.write(tag_segment)


def do_rehash(filename, ext):
    """
    Call the appropriate rehash function for the file extension.
    """
    if ext == "png":
        rehash_png(filename)
    elif ext == "jpg":
        rehash_jpg(filename)
    elif ext == "jpeg":
        rehash_jpg(filename)
    elif ext == "gif":
        rehash_gif(filename)
    elif ext == "webm":
        rehash_ebml(filename)
    elif ext == "mkv":
        rehash_ebml(filename)
    elif ext == "mp4":
        rehash_mp4(filename)
    else:
        pass


def is_filetype_supported(filename):
    """
    Check if a file type is valid and supported by rehash.
    If true, return the file extension.
    """
    MESSAGE_NO_FILE = "is not a valid file."
    MESSAGE_FILE_EXT_UNKNOWN = "couldn't determine the file type... check file extension?"
    MESSAGE_FILE_EXT_UNSUPPORTED = "file type is unsupported."
    
    if not os.path.isfile(filename):
        print(filename + " " + MESSAGE_NO_FILE)
        return None
    
    # get the filename file extension and compare to supported extensions
    FILETYPES = ("png", "jpg", "jpeg", "gif", "webm", "mkv")
    
    ext_split = os.path.splitext(filename)
    file_ext = ext_split[1]
    if (not file_ext) or file_ext == os.path.extsep:
        print(MESSAGE_FILE_EXT_UNKNOWN)
        return None
    file_ext = (file_ext[1:]).lower() # remove extension separator, make extension lower
    if file_ext not in FILETYPES:
        print(MESSAGE_FILE_EXT_UNSUPPORTED)
        return None
    # filetype is known and supported
    return file_ext
    

def get_rehash_filename(filename):
    """
    Return the filename rehash will write to if NOT overwriting filename.
    """
    pname, fname = os.path.split(filename)
    return os.path.join(pname, "rehash_" + fname)    
    
    
def main(argv):
    """
    """
    parser = argparse.ArgumentParser(description="Change the hash of a file.")
    parser.add_argument("-o", help="overwrite (write output to input file)", action="store_true")
    parser.add_argument("filenames", nargs="+", help="change the hash of these file(s)")
    args = parser.parse_args(argv[1:])
    
    filenames = args.filenames
    for fname in filenames:
        # print(fname)
        file_ext = is_filetype_supported(fname)
        if file_ext:
            if not args.o:
                new_fname = get_rehash_filename(fname)
                copyfile(fname, new_fname)
                fname = new_fname
            do_rehash(fname, file_ext)
        else:
            pass


if __name__ == "__main__":
    main(sys.argv)
