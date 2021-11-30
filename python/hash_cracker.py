import hashlib, termcolor, argparse
import regex as re

def crack(hash_type, hash_value, wordlist):

    with open(wordlist, "r") as f:
        f = f.readlines()
        for line in f:
            h = hashlib.new(hash_type)
            h.update(line.strip("\n").encode("utf-8"))

            if h.hexdigest() == hash_value:
                return line.strip("\n")

        return False

def detect_algorithm(hash):

    if re.findall(r"([a-fA-F\d]{128})", hash):
        return "sha512"
    elif re.findall(r"([a-fA-F\d]{64})", hash):
        return "sha256"
    elif re.findall(r"([a-fA-F\d]{40})", hash):
        return "sha1"
    if re.findall(r"([a-fA-F\d]{32})", hash):
        return "md5"

    else:
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("hash", help="hash to crack")
    parser.add_argument("-w", "--wordlist", help="wordlist to use", default="/opt/Hacking/SecLists/Passwords/probable-v2-top12000.txt")
    args = parser.parse_args()

    hash_type = detect_algorithm(args.hash)

    if hash_type:
        print(termcolor.colored("[*] Cracking {} hash".format(hash_type), "green"))
        print(termcolor.colored("[*] Hash: {}".format(args.hash), "green"))
        print(termcolor.colored("[*] Wordlist: {}".format(args.wordlist), "green"))

        result = crack(hash_type, args.hash, args.wordlist)

        if result:
            print(termcolor.colored("[*] Password found: {}".format(result), "green"))
        else:
            print(termcolor.colored("[*] Password not found", "red"))
    else:
        print(termcolor.colored("[*] Hash format not supported", "red"))

main()