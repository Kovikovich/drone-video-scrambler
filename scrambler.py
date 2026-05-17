import os
from PIL import Image

class LFSR:
    def __init__(self, seed):
        self.state = seed if seed != 0 else 0xACE1
        self.mask = 0x80000057 

    def next_bit(self):
        bit = self.state & 1
        if bit:
            self.state = (self.state >> 1) ^ self.mask
        else:
            self.state >>= 1
        return bit

    def get_random_int(self, max_val):
        if max_val <= 1:
            return 0
        bits_needed = max_val.bit_length()
        value = 0
        for _ in range(bits_needed):
            value = (value << 1) | self.next_bit()
        return value % max_val

def generate_permutation_map(num_blocks, seed):
    lfsr = LFSR(seed)
    permutation = list(range(num_blocks))
    
    for i in range(num_blocks - 1, 0, -1):
        j = lfsr.get_random_int(i + 1)
        permutation[i], permutation[j] = permutation[j], permutation[i]
        
    return permutation

def process_image(image_path, blocks_x, blocks_y, seed, mode="encrypt"):
    img = Image.open(image_path)
    img_w, img_h = img.size
    
    block_w = img_w // blocks_x
    block_h = img_h // blocks_y
    
    img = img.crop((0, 0, block_w * blocks_x, block_h * blocks_y))
    img_w, img_h = img.size
    
    blocks = []
    for y in range(blocks_y):
        for x in range(blocks_x):
            box = (x * block_w, y * block_h, (x + 1) * block_w, (y + 1) * block_h)
            blocks.append(img.crop(box))
            
    num_blocks = len(blocks)
    perm_map = generate_permutation_map(num_blocks, seed)
    
    result_img = Image.new(img.mode, (img_w, img_h))
    out_blocks = [None] * num_blocks
    
    for original_idx, scrambled_idx in enumerate(perm_map):
        if mode == "encrypt":
            out_blocks[scrambled_idx] = blocks[original_idx]
        else:
            out_blocks[original_idx] = blocks[scrambled_idx]
            
    idx = 0
    for y in range(blocks_y):
        for x in range(blocks_x):
            result_img.paste(out_blocks[idx], (x * block_w, y * block_h))
            idx += 1
            
    return result_img

if __name__ == "__main__":
    SECRET_SEED = 44257
    BLOCKS_X = 16
    BLOCKS_Y = 12
    
    INPUT_FILE = "original.jpg"
    ENCRYPTED_FILE = "encrypted.png"
    DECRYPTED_FILE = "decrypted.png"
    
    if os.path.exists(INPUT_FILE):
        encrypted_res = process_image(INPUT_FILE, BLOCKS_X, BLOCKS_Y, SECRET_SEED, mode="encrypt")
        encrypted_res.save(ENCRYPTED_FILE)
        
        decrypted_res = process_image(ENCRYPTED_FILE, BLOCKS_X, BLOCKS_Y, SECRET_SEED, mode="decrypt")
        decrypted_res.save(DECRYPTED_FILE)
