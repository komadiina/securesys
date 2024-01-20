import os, json, subprocess, glob
from user import User
from ca import CA
from OpenSSL import crypto
from dotenv import load_dotenv
from getpass import getpass
from datetime import datetime

load_dotenv()

class System:
    def register_user() -> User:
        print("Please provide your registration details (used for logon)")

        # Username (must be unique)
        username = input("Username: ")       
        user_folder = os.getenv('ROOT_DIR') + '/' + os.getenv('USER_FOLDER') + '/' + username
        if os.path.exists(user_folder):
                print(f'Username {username} is not available, please try again.')
                System.register_user()
                return
        else: os.mkdir(user_folder) 

        # Password (both must match)
        passwd = '_'
        pwd_verification = '__'        
        while passwd != pwd_verification:        
            passwd = getpass("Password: ")
            pwd_verification = getpass("Verify password: ")
        
            if passwd != pwd_verification:
                print("Passwords not matching, please try again.")
                
        # Generate an RSA key pair (AES-256 encryption standard)
        userkey = crypto.PKey()
        userkey.generate_key(crypto.TYPE_RSA, 2048)
        
        # Write private key
        privkey_path = f"{os.getenv('ROOT_DIR')}/{os.getenv('PRIVATE_FOLDER')}/{username}-private.key"
        with open(privkey_path, 'wt')as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, userkey).decode('utf-8'))
        
        # Write public key
        pubkey_path = f"{os.getenv('ROOT_DIR')}/{os.getenv('PRIVATE_FOLDER')}/{username}-public.key"
        with open(pubkey_path, 'wt') as f:
            f.write(crypto.dump_publickey(crypto.FILETYPE_PEM, userkey).decode('utf-8'))
        
        # Feedback
        print(f'Key pair generated: {privkey_path}, {pubkey_path}')
        
        # Generate a certificate request
        request = crypto.X509Req()
        subject = request.get_subject()
        
        # Prompt user for CSR details
        subject.C = input("Country name (2 letter code): ")
        subject.ST = input("State or province name: ")
        subject.L = input("Locality name: ")
        subject.O = input("Organization name: ")
        subject.OU = input("Organizational unit name: ")
        subject.CN = input("Your common name: ")
        subject.emailAddress = input("Your contact e-mail address: ")
        
        request.set_pubkey(userkey)
        request.sign(userkey, "sha256")
        
        # Write the certificate to file 
        csr_path = f"{os.getenv('ROOT_DIR')}/{'requests'}/{username}.csr"
        with open(csr_path, 'wt') as f:
            f.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, request).decode('utf-8'))
            
        # Invoke CA to (attempt to) sign the user CSR
        ca: CA = CA()
        ca.sign(csr_path, username)
        
        # Add user to ./res/usrlist
        usrlist_path = f'{os.getenv("ROOT_DIR")}/{os.getenv("USERLIST")}'
        with open(usrlist_path, 'a') as f:
            f.write(f'{username}\n')
        
        # Create user's environment
        ### history.json (entries)
        data = {"entry_history":[]}
        with open(f"{user_folder}/history.json", 'x') as f:
            json.dump(data, f)
        ### notifications.json
        data = {"notifications":list()}
        with open(f"{user_folder}/notifications.json", 'x') as f:
            json.dump(data, f)
            
        ### data.json (username, hashed_pwd, last_hash)
        data = {
                "username": username, 
                "password": System.__get_password_hash(passwd), 
                "last_hash": System.__get_file_hash(f"{user_folder}/notifications.json")
            }
        with open(f"{user_folder}/data.json", 'x') as f:
            json.dump(data, f)
        
    def user_logon() -> None:
        # Prompt user for certificate
        crt_path = input("Please define the path to your certificate file (omit / at beginning, to use certificates from ./certs/ folder): ")
        if crt_path.startswith('/') == False:
            crt_path = f'{os.getenv("ROOT_DIR")}/{os.getenv("CERTS_FOLDER")}/{crt_path}'
        
        # Check if certificate exists
        if os.path.exists(crt_path) == False:
            print(f"Given certificate (full path: {crt_path}) could not be located. Exiting...")
            return    
        
        with open(crt_path, 'rb') as f:
            crt = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
            
        # User certificate authentication 
        # Criteria: valid CA, not expired
        result = CA.authorize(crt)
        if result[0] == False:
            print(f"Unable to authorize the provided certificate, reason: {result[1]}")
            return
        
        # User verified OK, prompt for credentials
        username = input("Username: ")
        password = getpass()
        
        # Verify the password
        status = System.check_password(username, password)
        while status == False:
            print("[!!!] Incorrect password entered.")            
            password = input(f"Retry password: ")
            status = System.check_password(username, password)
            
        # User successfully logged on        
        # Cache current keypair
        basename=f"{os.getenv('ROOT_DIR')}/{os.getenv('PRIVATE_FOLDER')}/{username}"
        targetkeys = (f"{basename}-private.key", f"{basename}-public.key")
        subprocess.run(['cp', targetkeys[0], targetkeys[1], f"{os.getenv('ROOT_DIR')}/{os.getenv('CACHED_DIR')}/"])
            
        # Check for any file tampering (compare hashes to saved)
        System.check_tampering(username)
        
        # Prepare workspace
        user: User = System.instantiate_workspace(username)
        
        # Redirect the user to workspace
        user.dashboard()
        
        # Save user data
        System.save_userdata(user)
        
    def save_userdata(user: User):
        user_folder = f"{os.getenv('ROOT_DIR')}/{os.getenv('USER_FOLDER')}/{user.username}/"
        
        # combine user.history["entry_history"] (list) with user.new_encryptions (list) -> list
        # wrap around a single-entry dict/map
        combined = {"entry_history": user.history["entry_history"] + user.new_encryptions}
        user.history = combined
        
        # write new history.json
        with open(f"{user_folder}/history.json", 'w') as f:
            json.dump(combined, f)
        
        # find hash(history.json) and write into data.json
        new_hash = System.__get_file_hash(f"{user_folder}/history.json")
        
        # read data.json fields (username, passwd, last_hash)
        with open(f"{user_folder}/data.json", 'r') as f:
            userdata = json.load(f)
        
        # update previous hash to new one
        userdata["last_hash"] = new_hash
        
        # write newly updated fields
        with open(f'{user_folder}/data.json', 'w') as f:
            json.dump(userdata, f)        
            
        # Write user notifications
        with open(f'{user_folder}/notifications.json', 'w') as f:
            json.dump(user.notifications, f)
            
        # Clear cached keys
        for file in glob.glob(f'{os.getenv("ROOT_DIR")}/{os.getenv("CACHED_DIR")}/*'):
            os.remove(file)
        
    def instantiate_workspace(username) -> User:
        # Parse notifications
        user_folder = f"{os.getenv('ROOT_DIR')}/{os.getenv('USER_FOLDER')}/{username}"
        with open(f"{user_folder}/notifications.json", 'r') as f:
            notifications = json.load(f)
                    
        # Parse ciphering history
        with open(f"{user_folder}/history.json", 'r') as f:
            history = json.load(f)
        
        return User(username, history, notifications)
        
    def __get_password_hash(password) -> bool:
        hashed: str = subprocess.check_output(
            ['openssl', 'passwd', '-6', '-salt', "SGRNST", password]).decode().strip()
        return hashed.split('$')[3]
    
    def __get_file_hash(filename) -> str:
        return subprocess.check_output(['openssl', 'dgst', '-sha512', filename]) \
                .decode().strip().split(' ')[1]
        
        
    def check_password(username, password) -> bool:
        # Read user credentials (safely), from $user/data.json
        userfile = f"{os.getenv('ROOT_DIR')}/{os.getenv('USER_FOLDER')}/{username}/data.json"
        with open(userfile, 'r') as f:
            credentials_json = json.load(f)
        
        # Compare hash to stored password
        return System.__get_password_hash(password) == credentials_json["password"]
    
    def check_tampering(username) -> None:
        userfolder = f"{os.getenv('ROOT_DIR')}/{os.getenv('USER_FOLDER')}/{username}"
        with open(f"{userfolder}/data.json", 'r') as f:
            last_hash = json.load(f)["last_hash"]
            
        
        # Calculate current hash, split string by ' ', access the second entry (hash value)
        current_hash = subprocess.check_output(
            ['openssl', 'dgst', '-sha512', f"{userfolder}/history.json"]).decode().strip().split(' ')[1]
        
        print(last_hash)
        print(current_hash)
        
        # print(f"Last hash: {last_hash}\nCurrent hash: {current_hash}")
        
        if last_hash != current_hash:
            System.alert_user(username, content="External file tampering detected!")
            
    def alert_user(username, content) -> None:
        userfolder = f"{os.getenv('ROOT_DIR')}/{os.getenv('USER_FOLDER')}/{username}"
        
        # Load JSON data
        with open(f"{userfolder}/notifications.json", 'r') as f:
            ctr = json.load(f)
        
        # Create a new unread (read=False) notification and add it to the container
        date = datetime.now().strftime("%H:%M %d/%m/%Y")
        new_notification = {"read":False, "content":content, "date":date}
        ctr["notifications"].append(new_notification)
        
        # Dump the newly-updated JSON container
        with open(f"{userfolder}/notifications.json", 'w') as f:
            json.dump(ctr, f)