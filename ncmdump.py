import binascii
import struct
import base64
import json
import os
import sys
import glob
from Crypto.Cipher import AES
import asyncio

def existing_mp3(file_path):
    file_name = os.path.splitext(file_path)[0]    
    return os.path.exists(file_name + ".mp3") or os.path.exists(file_name + ".flac")

def dump(file_path):
    if existing_mp3(file_path):
        print('转换文件已存在，跳过')
        return
    # hex to str
    print(f'正在转换文件:{file_path}')
    core_key = binascii.a2b_hex("687A4852416D736F356B496E62617857")
    meta_key = binascii.a2b_hex("2331346C6A6B5F215C5D2630553C2728")
    unpad = lambda s: s[0:-(s[-1] if type(s[-1]) is int else ord(s[-1]))]
    f = open(file_path, 'rb')
    header = f.read(8)
    # str to hex
    assert binascii.b2a_hex(header) == b'4354454e4644414d'
    f.seek(2, 1)
    key_length = f.read(4)
    key_length = struct.unpack('<I', bytes(key_length))[0]
    key_data = f.read(key_length)
    key_data_array = bytearray(key_data)
    for i in range(0, len(key_data_array)):
        key_data_array[i] ^= 0x64
    key_data = bytes(key_data_array)
    cryptor = AES.new(core_key, AES.MODE_ECB)
    key_data = unpad(cryptor.decrypt(key_data))[17:]
    key_length = len(key_data)
    key_data = bytearray(key_data)
    key_box = bytearray(range(256))
    c = 0
    last_byte = 0
    key_offset = 0
    for i in range(256):
        swap = key_box[i]
        c = (swap + last_byte + key_data[key_offset]) & 0xff
        key_offset += 1
        if key_offset >= key_length:
            key_offset = 0
        key_box[i] = key_box[c]
        key_box[c] = swap
        last_byte = c
    meta_length = f.read(4)
    meta_length = struct.unpack('<I', bytes(meta_length))[0]
    meta_data = f.read(meta_length)
    meta_data_array = bytearray(meta_data)
    for i in range(0, len(meta_data_array)):
        meta_data_array[i] ^= 0x63
    meta_data = bytes(meta_data_array)
    meta_data = base64.b64decode(meta_data[22:])
    cryptor = AES.new(meta_key, AES.MODE_ECB)
    meta_data = unpad(cryptor.decrypt(meta_data)).decode('utf-8')[6:]
    meta_data = json.loads(meta_data)
    crc32 = f.read(4)
    crc32 = struct.unpack('<I', bytes(crc32))[0]
    f.seek(5, 1)
    image_size = f.read(4)
    image_size = struct.unpack('<I', bytes(image_size))[0]
    image_data = f.read(image_size)
    file_name = f.name.split("/")[-1].split(".ncm")[0] + '.' + meta_data['format']
    m = open(os.path.join(os.path.split(file_path)[0], file_name), 'wb')
    chunk = bytearray()
    while True:
        chunk = bytearray(f.read(0x8000))
        chunk_length = len(chunk)
        if not chunk:
            break
        for i in range(1, chunk_length + 1):
            j = i & 0xff
            chunk[i - 1] ^= key_box[(key_box[j] + key_box[(key_box[j] + j) & 0xff]) & 0xff]
        m.write(chunk)
    m.close()
    f.close()
    return file_name

def go_dump(file_list):
    for f in file_list:
        print(f'正在处理：{f}')
        dump(f)


if __name__ == '__main__':
    file_list = sys.argv[1:]
    for file in file_list:
        if os.path.isfile(file):
            print(f'正在处理：{file}')
            dump(file)
        elif os.path.isdir(file):
            files = glob.glob(os.path.join(os.path.join(file,'**'),'*.ncm'),recursive=True)
            go_dump(files)
