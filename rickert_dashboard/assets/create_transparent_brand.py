import zlib
import struct
import os

src_path = r"C:\Users\xanth\Dropbox\個人請負\品川区テニス連盟\hp\docs\rickert_dashboard\assets\brand_mark.png"
dst_path = r"C:\Users\xanth\Dropbox\個人請負\品川区テニス連盟\hp\docs\rickert_dashboard\assets\brand_mark_transparent.png"

def read_png(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Check signature
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError("Not a PNG file")
    
    idx = 8
    width, height = 0, 0
    idat_chunks = []
    
    while idx < len(data):
        length = struct.unpack('>I', data[idx:idx+4])[0]
        chunk_type = data[idx+4:idx+8]
        chunk_data = data[idx+8:idx+8+length]
        idx += 12 + length
        
        if chunk_type == b'IHDR':
            width, height, bit_depth, color_type, comp, filt, inter = struct.unpack('>IIBBBBB', chunk_data)
        elif chunk_type == b'IDAT':
            idat_chunks.append(chunk_data)
        elif chunk_type == b'IEND':
            break
            
    decompressed = zlib.decompress(b''.join(idat_chunks))
    
    # Parse scanlines (RGB or RGBA)
    bpp = 4 if color_type == 6 else 3
    stride = width * bpp + 1
    raw_pixels = bytearray()
    
    prev_line = bytearray(width * bpp)
    for y in range(height):
        line = decompressed[y * stride : (y + 1) * stride]
        filter_type = line[0]
        pixel_bytes = bytearray(line[1:])
        
        # Paeth / Sub / Up / Average unfiltering
        unfiltered = bytearray(width * bpp)
        for x in range(width * bpp):
            filt_val = pixel_bytes[x]
            left = unfiltered[x - bpp] if x >= bpp else 0
            up = prev_line[x]
            upper_left = prev_line[x - bpp] if x >= bpp else 0
            
            if filter_type == 0: # None
                val = filt_val
            elif filter_type == 1: # Sub
                val = (filt_val + left) & 0xFF
            elif filter_type == 2: # Up
                val = (filt_val + up) & 0xFF
            elif filter_type == 3: # Average
                val = (filt_val + ((left + up) >> 1)) & 0xFF
            elif filter_type == 4: # Paeth
                p = left + up - upper_left
                pa = abs(p - left)
                pb = abs(p - up)
                pc = abs(p - upper_left)
                if pa <= pb and pa <= pc: pr = left
                elif pb <= pc: pr = up
                else: pr = upper_left
                val = (filt_val + pr) & 0xFF
            else:
                val = filt_val
            unfiltered[x] = val
        prev_line = unfiltered
        raw_pixels.extend(unfiltered)
        
    return width, height, bpp, raw_pixels

def write_png_rgba(filepath, width, height, rgba_data):
    # Prepare scanlines with None filter (0)
    raw = bytearray()
    for y in range(height):
        raw.append(0) # Filter type None
        raw.extend(rgba_data[y * width * 4 : (y + 1) * width * 4])
        
    compressed = zlib.compress(raw, level=9)
    
    def make_chunk(ctype, cdata):
        return struct.pack('>I', len(cdata)) + ctype + cdata + struct.pack('>I', zlib.crc32(ctype + cdata) & 0xFFFFFFFF)
        
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    
    with open(filepath, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(make_chunk(b'IHDR', ihdr))
        f.write(make_chunk(b'IDAT', compressed))
        f.write(make_chunk(b'IEND', b''))

def create_transparent_brand():
    width, height, bpp, raw_pixels = read_png(src_path)
    rgba_out = bytearray(width * height * 4)
    
    for i in range(width * height):
        if bpp == 4:
            r, g, b, a = raw_pixels[i*4 : i*4+4]
        else:
            r, g, b = raw_pixels[i*3 : i*3+3]
            a = 255
            
        # Calculate Red dominance (Brand of Sacrifice is vibrant red)
        # Background is muted slate-gray (#2c3540: r~44, g~53, b~64)
        red_diff = max(0, int(r) - max(int(g), int(b)))
        brightness = (int(r) + int(g) + int(b)) / 3.0
        
        # Threshold for red mark vs gray background
        if red_diff > 18 or (r > 120 and r > g * 1.3 and r > b * 1.3):
            # Alpha based on red intensity
            alpha = min(255, int(red_diff * 2.8) + 40)
            # Vibrant Red Output with alpha
            rgba_out[i*4] = 255     # R
            rgba_out[i*4+1] = int(g * 0.3) # G
            rgba_out[i*4+2] = int(b * 0.3) # B
            rgba_out[i*4+3] = alpha # A
        else:
            # Completely Transparent Background
            rgba_out[i*4] = 0
            rgba_out[i*4+1] = 0
            rgba_out[i*4+2] = 0
            rgba_out[i*4+3] = 0
            
    write_png_rgba(dst_path, width, height, rgba_out)
    print(f"Created transparent brand icon: {dst_path} ({width}x{height})")

if __name__ == "__main__":
    create_transparent_brand()
