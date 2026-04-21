import serial
import os

# Configuration
SERIAL_PORT = 'COM14'
BAUD_RATE = 9600
PACKET_SIZE = 9

def main():
    # Force ANSI colors in Windows terminal
    os.system('')
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=None)
        print(f"Dumping raw {PACKET_SIZE}-byte chunks from {SERIAL_PORT}...")
        print("Press Ctrl+C to stop.\n")

        while True:
            # Read exactly 9 bytes (this will block until they arrive)
            raw = ser.read(PACKET_SIZE)
            
            # Convert to a space-separated Hex string
            hex_string = " ".join(f"{b:02X}" for b in raw)
            
            # Print the line and immediately flush to terminal
            print(f"LOG: {hex_string}", flush=True)

    except KeyboardInterrupt:
        print("\nDump stopped.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()