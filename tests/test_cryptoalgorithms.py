import sys
sys.path.append("../modules") # cryptoalgorithms module

import cryptoalgorithms as calg

def test_RFC():
    num_rails=3
    plaintext="testiranje"
    
    rfc = calg.RFC({"num_rails": num_rails})
    cipher = rfc.encrypt(plaintext) 
    
    print(f'RFC({plaintext}) = {cipher}')
    
def test_Myszkowski():
    key="biciklo"
    plaintext="mjesavina svega i svacega"
    
    myszk = calg.Myszkowski({"key": key})
    cipher = myszk.encrypt(plaintext)
    
    print(f'Myskowszki({plaintext}) = {cipher}')

def test_Playfair():
    key="ognjen"
    plaintext="mjesavina"
    
    playfair = calg.Playfair({"key": key})
    cipher = playfair.encrypt(plaintext) 
    
    print(f'Playfair({plaintext}) = {cipher}')
    
if __name__ == '__main__':
    print("1 - rfc, 2 - playfair, 3 - myskowszki > ", end='')
    sel=int(input())
    
    if sel == 1:
        test_RFC()
    if sel == 2:
        test_Playfair()
    if sel == 3:
        test_Myszkowski()