import argparse
import os

# Device info
# 1 page = (2k + 64)=2112 bytes
# 1 block = 64 pages
# 1 device = 1024 blocks = 65536 pages

PAGESIZE = 2112
BLOCKSIZE = PAGESIZE * 64

# return uppercase hex string without 0x, leading zero to 2 digits
def hexu(value):
    return str(hex(value))[2:].upper().zfill(2)

# return big endian 32 bit integer
def int32(blob, offset):
    value = (blob[offset] << 24) + (blob[offset+1] << 16) + (blob[offset+2] << 8) + (blob[offset+3])
    return value

# write big endian 32 bit integer
def writeint32(blob, value, offset):
    blob[offset + 0] = (value & 0xFF000000) >> 24
    blob[offset + 1] = (value & 0x00FF0000) >> 16
    blob[offset + 2] = (value & 0x0000FF00) >> 8
    blob[offset + 3] =  value & 0x000000FF
    return True

# swap bytes
def swap(blob):    
    blobsize = len(blob)
    pairs = blobsize >> 1
    new_blob = bytearray(blobsize)
    
    for offset in range(pairs):
        new_blob[(offset * 2) + 0] = blob[(offset * 2) + 1]
        new_blob[(offset * 2) + 1] = blob[(offset * 2) + 0]
    return new_blob

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Extract MIDI data from 837a08.7s (Gradius IV 68K Sound PRG ROM).')
    p.add_argument('input_file', type=str, help='Input file (e.g. 837a08.7s)')
    p.add_argument('output_directory', type=str, help='Output directory (e.g. midi)')
    args = p.parse_args()

    f1 = open(args.input_file, 'rb')    

    print('Reading ' + args.input_file + '...')
    data1 = f1.read()

    f1.close()
    
  
    if (len(data1) != 524288):
        print("ROM incorrect size error!")
    else:
        table_entries = 0xC5;
        table_offset = 0x7C00C;
        table_max = 0x75D9E;
        data2 = swap(data1)
    
        pointer_table = []
        sorted_table = []
        dupe_table = []
        
        for table_entry in range(table_entries):
            table_current_offset = table_offset + (table_entry * 0xA)
            ptr = int32(data2, table_current_offset)            
            pointer_table.append(ptr)
            if ptr in sorted_table:
                dupe_table.append(table_entry)        
            else:
                sorted_table.append(ptr)
        sorted_table.sort()
        sorted_table.append(table_max)
        
        os.makedirs(args.output_directory, exist_ok=True)
        
        for table_entry in range(table_entries):
            if (table_entry in dupe_table):
                print (hexu(table_entry) + ': dupe, skipping')
            else:
                index_in_sort = sorted_table.index(pointer_table[table_entry])
                if index_in_sort == 0:
                    print(hexu(table_entry) + ': zero pointer, skipping')
                else:
                    offset_into_data = pointer_table[table_entry]
                    data_ending = sorted_table[index_in_sort + 1]
                    print(hexu(table_entry) + ': writing data from ' + hexu(pointer_table[table_entry]) + ' to ' + hexu(sorted_table[index_in_sort + 1]))
                    f3 = open(args.output_directory + '/midi' + hexu(table_entry) + '.mid', 'wb')
                    f3.write(data2[offset_into_data:data_ending])
                    f3.close()

    print("Done.")
