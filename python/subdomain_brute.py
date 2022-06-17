from termcolor import colored
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import os, os.path, requests, argparse, threading, time
from tqdm import tqdm

class Error(Exception):
    pass

def verify(wordlist, domain, threads, output, hide_words):
    if os.path.exists(wordlist):
        tqdm.write(colored("[+]", 'green') +" Wordlist found: " + wordlist + " / Words: " + str(len(open(wordlist).readlines())))
    else:
        tqdm.write(colored("[-]", 'red') + " Wordlist not found: " + wordlist)
        exit()
    if output != "":
        open(output, "w").close()

    tqdm.write(colored("[+]", 'green') + f" Hiding content with {hide_words} words!")
    tqdm.write(colored("[+]", 'green') + f" Threads: {threads}")
    tqdm.write(colored("[+]", 'green') + f" Domain: {domain}")

def banner():
    tqdm.write(colored("""
    _____       __    ______                         
   / ___/__  __/ /_  / ____/___  _____________  _____
   \__ \/ / / / __ \/ /_  / __ \/ ___/ ___/ _ \/ ___/
  ___/ / /_/ / /_/ / __/ / /_/ / /  / /__/  __/ /    
 /____/\__,_/_.___/_/    \____/_/   \___/\___/_/ """, 'blue') + colored("    By K4oS#8387", 'red'))
    tqdm.write("\n\n")

def divide_chunks(l, n):

    for i in range(0, len(l), n): 
        yield l[i:i + n]

def query_subdomain(subdomains, domain, hide_words, ssl, output):
    if subdomains == "" or domain == "": raise Error("The arguments supplied to the query_subdomain function are empty. Please check them")
    global time_now
    global count
    for subdomain in tqdm(subdomains):
        count += 1

        if time.time()-time_now >= 60:
            tqdm.write(colored("[i] ", "yellow") + str(count) + " Requests per minute")
            count = 0
            time_now = time.time()

        headers = {"Host": subdomain + "." + domain}

        if ssl:
            url = "https://" + domain
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        else:
            url = "http://" + domain

        r = requests.get(url, headers=headers, allow_redirects=False, verify=False)

        if len(r.text.split()) != hide_words:
            tqdm.write(colored("[+]", 'green') + f" {subdomain}.{domain} | Words: " + str(len(r.text.split())) + " | Status Code: " + str(r.status_code))
            if output != "":
                with open(output, "r") as f:
                    f.write(colored("[+]", 'green') + f" {subdomain}.{domain} | Words: " + str(len(r.text.split())) + " | Status Code: " + str(r.status_code) + "\n")

parser = argparse.ArgumentParser(description='Script to bruteforce subdomains')
parser.add_argument('--threads', help='Threads for enumeration subdomains. Default -> 10', type=int, default=10, required=False)
parser.add_argument('--domain', help='domain to bruteforce', type=str, default="", required=True)
parser.add_argument('--wordlist', help='Wordlist to use for subdomains', type=str, default="", required=True)
parser.add_argument('--output', help='Output file', type=str, default="", required=False)
parser.add_argument('--hw', help='Hide amount of words from output', type=int, required=False, default=0)
parser.add_argument('--ssl', help='Use https', type=bool, required=False, default=False)
args = parser.parse_args()

threads = args.threads
domain = args.domain
wordlist = args.wordlist
output = args.output
hide_words = args.hw
ssl = args.ssl

count = 0
time_now = time.time()

if __name__ == "__main__":
    banner()
    verify(wordlist, domain, threads, output, hide_words)

    tqdm.write(colored("[i]", 'yellow') + " Starting to enumerate subdomains...\n")
    with open(wordlist, 'r') as f:
        f = f.read().splitlines()
        try:
            for subdomains in list(divide_chunks(f, len(f)//threads+1)):
                t = threading.Thread(target=query_subdomain, args=(subdomains, domain, hide_words, ssl, output))
                t.start()
                t.join(0.5)
        except KeyboardInterrupt:
            tqdm.write(colored("[-]", 'red') + " Exiting...")
            exit(0)
    tqdm.write(colored("[i]", 'yellow') + " Finished starting threads!")
