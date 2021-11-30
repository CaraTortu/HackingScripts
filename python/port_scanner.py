import socket, argparse, termcolor, threading

open_ports = []

def get_open_ports(host, ports):

    global open_ports
    
    for port in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((host, port))
            open_ports.append(port)
            print(f"{termcolor.colored('[+] Open:', 'green')} {port}")
            s.close()
        except:
            pass
    return open_ports

def divide_chunks(l, n):

    for i in range(0, len(l), n): 
        yield l[i:i + n]

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--threads", help="Number of threads", type=int, default=10)
parser.add_argument("-p", "--ports", help="Ports to scan", type=list, default=range(1, 65536))
parser.add_argument("-i", "--ip", help="IP to scan", type=str, default="", required=True)
    
args = parser.parse_args()
host = args.ip
ports = args.ports
threads = args.threads

print(f"[+] Scanning {host}")

chunks = list(divide_chunks(ports, len(ports)//threads+1))

for i in range(threads):
    t = threading.Thread(target=get_open_ports, args=(host, chunks[i]))
    t.start()
    t.join(0.1)
