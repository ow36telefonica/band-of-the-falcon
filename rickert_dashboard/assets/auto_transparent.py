# auto_transparent.py - Erica Asset Auto Transparent Pipeline
import zlib
import struct
import sys
import os

def convert_to_transparent(src_path, dst_path):
    if not os.path.exists(src_path):
        print(f"Source file not found: {src_path}")
        return False
        
    print(f"[エリカ] 画像 ({os.path.basename(src_path)}) の背景自動透過切り抜きを開始するよ！")
    # Execute the PNG isolation logic
    import create_transparent_brand
    create_transparent_brand.src_path = src_path
    create_transparent_brand.dst_path = dst_path
    create_transparent_brand.create_transparent_brand()
    print(f"[エリカ] ピカピカの透過PNG ({os.path.basename(dst_path)}) が完成したよ！")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 2:
        convert_to_transparent(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python auto_transparent.py <src_png> <dst_png>")
