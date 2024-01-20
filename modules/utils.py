import os, dotenv

dotenv.load_dotenv()

def split(list, parts):
    k, m = divmod(len(list), parts)
    return (list[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(parts))

def get_matrix_column(matrix, idx: int) -> str:
    num_rows = len(matrix)
    
    text = ''
    
    for i in range(num_rows):
        try:
            text += matrix[i][idx]
        except IndexError:
            # (Myszkowski) if the matrix is not padded IndexError occurs
            continue
        
    return text

def get_matrix_cols_parallel(matrix, indices: list) -> str:
    num_rows = len(matrix)
    text = ''
    
    
    for j in range(0, num_rows):
        for i in range(0, len(matrix[j])):
            try:
                if i in indices:
                    text += matrix[j][i]
            except IndexError:
                continue
            
    return text   

def get_matching_indices(target_list: list, idx: int) -> list:
    result = list()
    for i in range(0, len(target_list)):
        if target_list[i] == idx:
            result.append(i)
            
    return result
                
                
def get_serial_number():
    file = f"{os.getenv('ROOT_DIR')}/{os.getenv('SERIAL_FILE')}"
    with open(file, 'rt') as f:
        current_number = int(f.read(), base=16)
        next_number = hex(current_number + 1)
        
    with open(file, 'wt') as f:
        f.write(str(next_number)[2:])
        
    return current_number


def readfile(filepath_encrypted: str):
    # TODO
    # all files are encrypted via AES-256-CBC
    # cmdline openssl invocation
    pass

def writefile(filepath_plaintext: str):
    # TODO
    # all files are to be encrypted via AES-256-CBC
    # cmdline openssl invocation
    pass