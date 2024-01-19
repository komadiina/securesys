import sys
sys.path.append("..") # cryptoalgorithms module

import cryptoalgorithms as calg

def test_RFC(input=False):
    num_rails=3
    plaintext="testiranje"
    
    if input:
        print("num_rails=", end='')
        num_rails=int(input())
        
        print("plaintext=", end='')
        plaintext=str(input())
    
    rfc = calg.RFC({"num_rails": num_rails})
    cipher = rfc.encrypt(plaintext) 
    print(cipher)
    
def test_Myszkowski():
    key="biciklo"
    myszk = calg.Myszkowski({"key": key})
    cipher = myszk.encrypt("mjesavina svega i svacega")
    pass

def test_Playfair():
    key="ognjen"
    playfair = calg.Playfair({"key": key})
    print(playfair.encrypt("mjesavina"))

if __name__ == '__main__':
    print("1 - rfc, 2 - playfair, 3 - myskowszki > ", end='')
    sel=int(input())
    
    if sel == 1:
        test_RFC()
    if sel == 2:
        test_Playfair()
    if sel == 3:
        test_Myszkowski()