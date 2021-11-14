from termcolor import colored
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import os, os.path, requests, argparse, threading, time
from tqdm import tqdm

class Error(Exception):
    pass

def verify(wordlist, url, threads, output, extensions, bl):
    if os.path.exists(wordlist):
        tqdm.write(colored("[+]", 'green') +" Wordlist found: " + wordlist + " / Words: " + str(len(open(wordlist).readlines())*(len(extensions) if extensions != "" else 1)))
    else:
        tqdm.write(colored("[-]", 'red') + " Wordlist not found: " + wordlist)
        exit()
    if output != "":
        open(output, "w").close()

    extensions = ",".join([extension for extension in extensions])

    url = url.rstrip("/")

    tqdm.write(colored("[+]", 'green') + f" Appending {extensions} extension/s!") if extensions != "" else None
    tqdm.write(colored("[+]", 'green') + f" Blacklisting {bl} status code/s!")
    tqdm.write(colored("[+]", 'green') + f" Threads: {threads}")
    tqdm.write(colored("[+]", 'green') + f" url: {url}")

def banner():
    tqdm.write(colored("""
    ____  _      ______                         
   / __ \(_)____/ ____/___  _____________  _____
  / / / / / ___/ /_  / __ \/ ___/ ___/ _ \/ ___/
 / /_/ / / /  / __/ / /_/ / /  / /__/  __/ /    
/_____/_/_/  /_/    \____/_/   \___/\___/_/ """, 'blue') + colored("    By K4oS#8387", 'red'))
    tqdm.write("\n\n")

def divide_chunks(l, n):

    for i in range(0, len(l), n): 
        yield l[i:i + n]

def query_url(dirs, url, bl, ext, output):
    url = url + "/"
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    if dirs == "" or url == "": raise Error("The arguments supplied to the query_folder function are empty. Please check them")
    global time_now
    global count

    for file in tqdm(dirs*(len(ext) if ext != "" else 1)):
        for fil in [file+exte for exte in ext] if ext != "" else [file]:
            count += 1

            if time.time()-time_now >= 60:
                tqdm.write(colored("[i] ", "yellow") + str(count) + " Requests per minute")
                count = 0
                time_now = time.time()

            url2 = url + fil
            r = requests.get(url2, allow_redirects=False, verify=False)
            if str(r.status_code) not in bl.split(","):
                tqdm.write(colored("[+]", 'green') + f" {url2} | Words: " + str(len(r.text.split())) + " | Status Code: " + str(r.status_code))
                if output != "":
                    f = open(output, "a")
                    f.write(colored("[+]", 'green') + f" {url2} | Words: " + str(len(r.text.split())) + " | Status Code: " + str(r.status_code) + "\n")
                    f.close()

parser = argparse.ArgumentParser(description='Script to bruteforce subdomains')
parser.add_argument('--threads', help='Threads for enumeration subdomains. Default -> 10', type=int, default=10, required=False)
parser.add_argument('--url', help='url to bruteforce', type=str, default="", required=True)
parser.add_argument('--wordlist', help='Wordlist to use for subdomains', type=str, default="", required=True)
parser.add_argument('--extensions', help='extensions to use for each wordlist entry', type=str, default="", required=False)
parser.add_argument('--output', help='Output file', type=str, default="", required=False)
parser.add_argument('--bl', help='Blacklist status codes', type=str, required=False, default="404")
args = parser.parse_args()

threads = args.threads
url = args.url
wordlist = args.wordlist
extensions = args.extensions
output = args.output
bl = args.bl

count = 0
time_now = time.time()

if __name__ == "__main__":
    banner()
    verify(wordlist, url, threads, output, extensions.split(","), bl)

    tqdm.write(colored("[i]", 'yellow') + " Starting to enumerate directories...\n")
    with open(wordlist, 'r') as f:
        f = f.read().splitlines()
        try:
            for sub in list(divide_chunks(f, len(f)//threads+1)):
                t = threading.Thread(target=query_url, args=(sub, url, bl, extensions.split(","), output))
                t.start()
                t.join(0.5)
        except KeyboardInterrupt:
            tqdm.write(colored("[-]", 'red') + " Exiting...")
            exit(0)
    tqdm.write(colored("[i]", 'yellow') + " Finished starting threads!")