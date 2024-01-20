import re, utils
from abc import abstractmethod
from math import ceil


class Cryptoalg:
    def __init__(self, parameters: dict={}):
        self.parameters = parameters
        
    @abstractmethod
    def encrypt(self, plaintext: str) -> str:
        pass
    
    @abstractmethod
    def decrypt(self, ciphertext: str) -> str:
        pass
    
    @abstractmethod
    def preprocess(self, plaintext: str) -> str:
        return plaintext.replace(' ', '')
    
    def set_parameters(self, new_params: dict):
        self.parameters = new_params
        

    
        
class RFC(Cryptoalg):
    def __init__(self, parameters: dict):
        super().__init__(parameters)
        
    def encrypt(self, plaintext: str) -> str:
        # parameters        
        num_rails = self.parameters["num_rails"]
        
        # base elements
        plaintext = self.preprocess(plaintext)
        length = len(plaintext)
        matrix = [['' for _ in range(num_rails)] for _ in range(length)]
        cipher = ''
                
        # Fill rail-
        direction: int = -1 # {-1, +1}
        y_pos = 0
        for i in range(0, length):
            if y_pos == 0 or y_pos == num_rails - 1:
                direction *= (-1)

            matrix[i][y_pos] = plaintext[i]  

            y_pos += direction
        
        
        # Parse cipher
        for j in range(0, num_rails):
            for i in range(0, length):
                if matrix[i][j] != '':
                    cipher += matrix[i][j]                
        
        return cipher
    
    def decrypt(self, ciphertext: str) -> str:
        pass        
    
class Myszkowski(Cryptoalg):
    def __init__(self, parameters: dict):
        super().__init__(parameters)
        
    def __enumerate_key(self, key: str) -> list:        
        # Sort and remove duplicates
        sorted_key = "".join(sorted(key))
        while re.search(r'([a-z])(.*)\1', sorted_key):
            sorted_key = re.sub(r'([a-z])(.*)\1', r'\1\2', sorted_key)
        
        i = 0 # 0-indexing, instead of 1-indexing
        enumeration_map = dict()
        for k in sorted_key:
            enumeration_map[k] = i
            i += 1
            
        # Enumerate all characters in key via enumeration_map into a list
        enumeration_list = list()
        for k in key:
            enumeration_list.append(enumeration_map[k])
        
        return enumeration_list
        
    def encrypt(self, plaintext: str, pad=True, padding: str = 'x') -> str:
        # keyschedule
        key = self.parameters["key"]
        key_enumerated = self.__enumerate_key(key)
        
        # prep plaintext (remove spaces, optional but yea)
        plaintext = plaintext.replace(' ', '')

        # additional post-calculated parameters
        num_cols = len(key_enumerated)
        num_rows = ceil(len(plaintext) / num_cols)
        
        # Pad with nullchars if needed
        if pad:
            remainder = num_cols * num_rows - len(plaintext)
            
            if remainder:
                print(f'Padding with amount={remainder} character={padding}')
                for i in range(remainder):
                    plaintext += padding

        # Fill the matrix
        matrix = list()
        i = 0
        while i < len(plaintext):
            matrix.append(list(plaintext[i:num_cols + i]))
            i += num_cols

                
        # Read out the cipher
        # ===================
        # this algorithm was made by o(n^2) gang
        # ===================
        i = 0
        cipher = ''
        while i <= max(key_enumerated):
            cipher += utils.get_matrix_cols_parallel(matrix=matrix, 
                                                    indices=utils.get_matching_indices(key_enumerated, i))
            i += 1
            
        return cipher            
    
    def decrypt(self, cipthertext: str) -> str:
        pass
    
class Playfair(Cryptoalg):
    def __init__(self, parameters: dict):
        super().__init__(parameters)
        
        # Initialize matrix right away
        self.__prepare_matrix(self.parameters["key"])
        
    def preprocess(self, key):
        # remove duplicate letters
        key = key.replace('j', 'i')
        while re.search(r'([a-z])(.*)\1', key):
            key = re.sub(r'([a-z])(.*)\1', r'\1\2', key)
            
        return key
    
    def __prepare_matrix(self, key):
        key = self.preprocess(self.parameters["key"])  
        self.matrix = list("abcdefghiklmnopqrstuvwxyz")
        for k in key:
            try:
                self.matrix.remove(k)
            except ValueError: # already deleted
                continue

        self.matrix = list(key) + self.matrix
        self.matrix = list(utils.split(self.matrix, 5))
    
    def __matrixfindpos(self, letter) -> (int, int):
        for x in range(len(self.matrix)):
            for y in range(len(self.matrix[x])):
                if self.matrix[y][x] == letter:
                    return (y, x) 
        
        # Should never happen
        return (-1, -1)
    
    def __substitute(self, a, b):
        a_pos = self.__matrixfindpos(a)
        b_pos = self.__matrixfindpos(b)
                    
        x1 = a_pos[1]
        x2 = b_pos[1]
        y1 = a_pos[0]
        y2 = b_pos[0]
        # repeating digram: shift first right, shift second up
        # (x1, y1), (x2, y2)                -> (x1, y2), (x2, y1)
        # (x1, y1), (x2, y1) (horizontalno) -> ((x1 + 1) % 5, y1), ((x2 + 1) % 5, y1) 
        # (x1, y1), (x1, y2) (vertikalno)   -> (x1, (y1 + 1) % 5), (x1, (y2 + 1) % 5)
        
        if x1 != x2 and y1 != y2:
            return self.matrix[y1][x2] + self.matrix[y2][x1] 
        elif x1 != x2 and y1 == y2:
            return self.matrix[y1][(x1 + 1) % 5] + self.matrix[y1][(x2 + 1) % 5]
        elif x1 == x2 and y1 != y2:
            return self.matrix[(y1 + 1) % 5][x1] + self.matrix[(y2 + 1) % 5][x1]
        else: # AA
            return self.matrix[y1][(x1 + 1) % 5] + self.matrix[(y1 - 1) % 5][x2]
    
    def encrypt(self, plaintext: str, padding_char='x') -> str:
        if len(plaintext) % 2:
            print(f'Uneven length of plaintext ({len(plaintext)}), using padding character: {padding_char}')
            plaintext += padding_char
        
        # preprocess plaintext
        plaintext = plaintext.replace('j', 'i')
        plaintext = plaintext.replace(' ', '')
        plaintext = plaintext.lower()
        
        cipher = ''
    
        # Split plaintext into pairs
        plaintext = list(utils.split(plaintext, len(plaintext) // 2))
        
        # Encrypt
        for (first, second) in plaintext:
            cipher += self.__substitute(first, second)     

        return cipher
    
    def decrypt(self, plaintext: str) -> str:
        pass
    
    
    
    
    
    
    
    
    
    
    
    