import sys
import socket

def send_state(state, port=9999):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(state.encode('utf-8'), ("127.0.0.1", port))
        print(f"Sent state '{state}' to 127.0.0.1:{port}")
    except Exception as e:
        print(f"Error sending state: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python send_state.py <permission|complete|busy|off>")
        sys.exit(1)
    
    send_state(sys.argv[1])
