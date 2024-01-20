from dotenv import load_dotenv
from cryptoalgorithms import *
import subprocess

load_dotenv()

class User:
    def __init__(self, username, history, notifications):
        # General user informations
        self.username: str = username
        self.history: dict = history
        self.notifications: dict = notifications
        
        # Current progress
        self.new_encryptions: list = list() # list[encryption_entry, ...]
        # encryption_entry = {plaintext, algorithm, key, ciphertext}
        
    def dashboard(self):
        subprocess.run(['clear'])
        print(f"------------------ Welcome, {self.username}! ------------------")
        self.check_for_notifications(self.notifications)
        
        # Main user menu
        sel = input(
            f"[1] - Encryption\n[2] - Show encryption history\n[3] - Show notification history\n[4, Q] - Logout\n> ").lower()
        
        while sel != '4' and sel != 'q':
            if sel == "1":
                self.encryption()
            elif sel == "2":
                self.encryption_history()
            elif sel == "3":
                self.notification_history()
            else: 
                print("Invalid input, please try again.")
            
            sel = input(
                f"[1] - Encryption\n[2] - Show encryption history\n[3] - Show notification history\n[4, Q] - Logout\n> ").lower()

        

        print("Exiting...")

    def encryption(self):
        sel = input(
            "[1] - Rail Fence Cipher\n[2] - Myzskowski Transposition\n[3] - Playfair\n[4, B] - Back\n> ").lower()
        
        while sel not in {'4', 'b'}:
            if sel == "1":
                # RFC
                key = int(input("Enter the number of rails: "))
                rfc = RFC({"key":key})
                
                plaintext = input("Enter text to encipher (max. 100 chars): ")
                while len(plaintext) > 100:
                    plaintext = input("Enter text to encipher (max. 100 chars): ")
                
                ciphertext = rfc.encrypt(plaintext)
                print(f'RFC({key}, {plaintext}) = {ciphertext}')
                
                # Save entry (for history.json)
                self.save_entry("RFC", str(key), plaintext, ciphertext)
            if sel == "2":
                # Myszkowski
                key = input("Enter your key: ")
                myszk = Myszkowski({"key":key})
                
                plaintext = input("Enter text to encipher (max. 100 chars): ")
                while len(plaintext) > 100:
                    plaintext = input("Enter text to encipher (max. 100 chars): ")
                
                ciphertext = myszk.encrypt(plaintext)
                print(f'Myszkowski({key}, {plaintext}) = {ciphertext}')
                
                self.save_entry("Myszkowski", key, plaintext, ciphertext)
            if sel == "3":
                # Playfair
                key = input("Enter your key: ")
                playfair = Playfair({"key":key})
                
                plaintext = input("Enter text to encipher (max. 100 chars): ")
                while len(plaintext) > 100:
                    plaintext = input("Enter text to encipher (max. 100 chars): ")
            
                ciphertext = playfair.encrypt(plaintext)
                print(f"Playfair({key}, {plaintext}) = {ciphertext}")
                
                self.save_entry("Playfair", key, plaintext, ciphertext)             
            
            sel = input(
                        "[1] - Rail Fence Cipher\n[2] - Myzskowski Transposition\n[3] - Playfair\n[4, B] - Back\n> ").lower()  
        
    def encryption_history(self):
        # Previous encryptions
        print("Previous encryptions:")
        if len(self.history["entry_history"]):
            for elem in self.history["entry_history"]:
                print("<--------------->")
                print(f'Algorithm: {elem["algorithm"]}')
                print(f'Key: {elem["key"]}')
                print(f'Plaintext: {elem["plaintext"]}')
                print(f'Ciphertext: {elem["ciphertext"]}')
                print("<--------------->")
        else:
            print("None.")
        
        # Current sessions encryptions
        print("New encryptions: ")
        if len(self.new_encryptions):
            for elem in self.new_encryptions:
                print("<--------------->")
                print(f'Algorithm: {elem["algorithm"]}')
                print(f'Key: {elem["key"]}')
                print(f'Plaintext: {elem["plaintext"]}')
                print(f'Ciphertext: {elem["ciphertext"]}')
                print("<--------------->")
        else:
            print("None.")
            
        return
    
    def notification_history(self):
        print("Notifications: ")
        for notif in self.notifications["notifications"]:
            print("<--------------->")
            print(f"Date: {notif['date']}")
            print(f"Read? {notif['read']}")
            print(f"> {notif['content']}")
            print("<--------------->")
        return
    
    def save_entry(self, algorithm, key, plaintext, ciphertext):
        entry = {
            "algorithm": algorithm,
            "key": key,
            "plaintext": plaintext,
            "ciphertext": ciphertext
        }
        self.new_encryptions.append(entry)
        # self.history["entry_history"].append(entry)
    
    def check_for_notifications(self, notifications, anticriteria=True):
        for notif in notifications["notifications"]:
            if notif["read"] != anticriteria:
                self.display_notification(notif)
                
    def display_notification(self, notification):
        print(f"--- {notification['date']} ---\n{notification['content']}")
        
        # Don't show in future
        notification['read'] = True