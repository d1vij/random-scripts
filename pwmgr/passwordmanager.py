import pyperclip
import json
import argparse
import chalk
from  cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
import hashlib
import random

pwFile = "d://scripts/pw.json"

def load_key() -> bytes:
    try:
        with open('key','r') as file:
            return bytes.fromhex(file.readline())
    except FileNotFoundError:
        print(f"{chalk.red("No key found!")}, generate new using --generate-key flag")
        exit()
        
def generate_password() -> str:
    return hashlib.sha256(random.randbytes(64)).hexdigest()
    
        
        

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--get','-g',type=str,nargs=1,help="Gets password for provided key",metavar="key")
    group.add_argument('--set','-s',type=str,nargs=2,help=f"Sets password for provided key {chalk.green("(Example use -> 'set google 1234' key here is google)")}", metavar=('key','value'))
    
    group.add_argument("--list",'-l',action="store_true",help="List stored keys")
    
    group.add_argument('--generate-password','-p',action="store_true",help=f"Generate and copy a new password {chalk.yellow("(i) ")}")
    group.add_argument("--generate-key",action='store_true',help=f"Generates a new secret key and stores it in the key file. {chalk.red("WARNING -> All existing stored passwords would become inaccessible upon key reset")}")
    
    
    args = parser.parse_args()

    try:
        with open(pwFile,'r',encoding='utf-8') as file:
            passwords = json.loads(file.read())
    except FileNotFoundError:
        open(pwFile,'x+').write("{}")
        passwords = {}
        
    if(args.get):
        #fetch password
        f = Fernet(load_key())
        _arg = args.get
        try:
            if(_arg[0] in passwords.keys()):
                pw = f.decrypt(bytes.fromhex(passwords[_arg[0]]))
                print(f"Password for {_arg[0]} : {chalk.green(pw)}")
                pyperclip.copy(pw.decode('utf-8'))
            else:
                print(chalk.red(f"No pasword stored for key {_arg[0]} !"))
        except InvalidToken as e:
            print(chalk.red(f"Cannot access stored password for key {chalk.green(_arg[0])}"),chalk.red("since it was stored using a different key. Re-set it using --set argument"))
    elif(args.set):
        _arg = args.set 
        f = Fernet(load_key())
        if(_arg[0] in passwords.keys()):
            if not (input(f"Key {chalk.green(_arg[0])} has a stored password. Do you want to {chalk.red("overwrite")} stored password?({chalk.green('yes')},{chalk.red('no')}) : ").lower().strip() == 'yes'):
                return
        _encrypted = f.encrypt(_arg[1].encode()).hex()
        passwords[_arg[0]]=_encrypted   
        
        with open('pw.json','w') as file:
            file.write(json.dumps(passwords))
        
        print(chalk.green(f"Saved password for {_arg[0]} as {_arg[1]}"))
    elif(args.generate_key):
        if(input(chalk.red(f"WARNING -> Generate a new key ? All existing passwords would become inaccessible!{chalk.green("(yes/no)")} : ")).strip().lower() == 'yes'):
            key_hex = Fernet.generate_key().hex()
            with open('key','w') as file:
                file.write(key_hex)
            print(f"Stored new key {chalk.green(key_hex)}")
    elif(args.list):
        print(chalk.green("Available keys:"))
        _available = sorted(passwords.keys())
        for entry in _available:
            print('→',chalk.yellow(entry))
    elif args.generate_password:
        p = generate_password()
        pyperclip.copy(p)
        print(f"Generated password -> {chalk.yellow(p)}")
            
def setup() -> None:
    # generates a encryption key and stores it as an hex string
    key_hex = Fernet.generate_key().hex()
    with open('key','w') as file:
        file.write(key_hex)
    with open('d://scripts/pw.json','w') as file:
        file.write('{}')
    
    
if __name__ == "__main__":
    main()