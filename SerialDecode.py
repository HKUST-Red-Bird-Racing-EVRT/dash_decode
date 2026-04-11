import serial
import struct
import time
import os
from datetime import datetime

# Configuration
SERIAL_PORT = 'COM8' 
BAUD_RATE = 9600
PACKET_SIZE = 9  # 1 byte (ID+Sync) + 8 bytes Data
SYNC_MASK = 0xFC # 11111100 in binary
SYNC_BITS = 0xA8 # 10101000 in binary (The pattern to match)

device_registry = {}

def format_hex(data):
    return " ".join(f"{b:02X}" for b in data)

def update_display():
    print("\033[H", end="") 
    print(f"{'--- BIT-SYNC ARDUINO MONITOR ---':^85}")
    print(f"{'Raw ID (Hex)':<14} | {'ID #':<6} | {'Count':<8} | {'Cycle (ms)':<12} | {'Data'}")
    print("-" * 95)
    
    for raw_id in sorted(device_registry.keys()):
        entry = device_registry[raw_id]
        cycle_str = f"{entry['cycle'] * 1000:8.2f}" if entry['cycle'] > 0 else "  ---"
        
        # entry['clean_id'] is the 0-3 value extracted from the byte
        print(f"{raw_id:<14} | {entry['clean_id']:<6} | {entry['count']:<8} | {cycle_str:<12} | {format_hex(entry['payload'])}")
    print(" " * 95) 

def main():
    os.system('') 
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
        print(f"Connected to {SERIAL_PORT}. Hunting for bit-pattern 101010xx...")
        os.system('cls' if os.name == 'nt' else 'clear')
        
        while True:
            if ser.in_waiting >= PACKET_SIZE:
                # Peek at the first byte in the buffer
                first_byte = ser.read(1)
                
                # Apply mask to see if the first 6 bits match 101010
                if (ord(first_byte) & SYNC_MASK) == SYNC_BITS:
                    # Sync confirmed! Read the remaining 8 bytes of data
                    payload = ser.read(8)
                    
                    if len(payload) == 8:
                        raw_id_hex = f"0x{ord(first_byte):02X}"
                        # Extract the actual ID (the last 2 bits)
                        clean_id = ord(first_byte) & 0x03 
                        
                        current_time = time.time()
                        
                        if raw_id_hex in device_registry:
                            prev = device_registry[raw_id_hex]
                            cycle_time = current_time - prev['time']
                            msg_count = prev['count'] + 1
                        else:
                            cycle_time = 0.0
                            msg_count = 1
                        
                        device_registry[raw_id_hex] = {
                            'clean_id': clean_id,
                            'time': current_time,
                            'stamp': datetime.now().strftime("%H:%M:%S"),
                            'payload': payload,
                            'cycle': cycle_time,
                            'count': msg_count
                        }
                        update_display()
                else:
                    # Not the start of a frame, skip this byte and keep hunting
                    continue

    except KeyboardInterrupt:
        print("\n\nMonitor stopped.")
    except Exception as e:
        print(f"\n\nError: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
