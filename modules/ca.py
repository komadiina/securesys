import os, utils, json, datetime
from OpenSSL import crypto
from dotenv import load_dotenv

load_dotenv()

class CA:
    def __init__(self):
        self.certpath = os.getenv('ROOT_DIR') + '/' + os.getenv('CA_CERT')
        self.keypath = os.getenv('ROOT_DIR') + '/' + os.getenv('CA_KEY')
    
    def sign(self, csr_path, username):
        # Called automatically when a user registers
        
        # Load the CA certificate        
        with open(self.certpath, 'rt') as cafile:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cafile.read())
        
        # Load the CA PKey
        with open(self.keypath, 'rt') as cafile:
            ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, cafile.read())
            
        # Load the CSR file
        with open(csr_path, 'rt') as csrfile:
            csr = crypto.load_certificate_request(crypto.FILETYPE_PEM, csrfile.read())
        
        # Create a new certificate to be signed
        newcert = crypto.X509()
        newcert.set_subject(csr.get_subject())
        newcert.set_pubkey(csr.get_pubkey())
        newcert.set_serial_number(utils.get_serial_number())
        
        days_valid = (3 * 31) * 24 * 60 * 60 # 3 months
        newcert.gmtime_adj_notBefore(0)
        newcert.gmtime_adj_notAfter(days_valid)

        newcert.set_issuer(ca_cert.get_subject())
        newcert.sign(ca_key, "sha256")
        
        newcert_path = f"{os.getenv('ROOT_DIR')}/{os.getenv('CERTS_FOLDER')}/{username}.crt"
        with open(newcert_path, "wt") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, newcert).decode('utf-8'))
        
        # Feedback
        print(f"CA: Certificate signed, path: {newcert_path}")
        
        # Mark the certificate as .old after signing
        os.rename(csr_path, csr_path + ".old")    
        
        return newcert
    
    @staticmethod
    def authorize(cert: crypto.X509) -> (bool, str):
        # Certificate must not be expired
        if cert.has_expired():
            return (False, "Certificate has expired")
        
        # Certificate must not be revoked 
        # TODO (simple crl)
        
        crl: crypto.CRL = CA.load_crl()
        for r in crl.get_revoked():
            if r.get_serial() == cert.get_serial_number():
                return (False, f"Certificate has been revoked (reason: {r.get_reason()})")
        
        # Load the CA certificate        
        ca: CA = CA()
        with open(ca.certpath, 'rt') as cafile:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cafile.read())
        
        # Verify the authenticity of given certificate
        if ca_cert.get_subject() != cert.get_issuer():
            return (False, "Certificate has not been issued by local CA")

        return (True, None)    
    
    @staticmethod
    def revoke(cert: crypto.X509, reason: bytes = None):
        # Instantiate a revoked X509 certificate 
        revoked = crypto.Revoked()
        revoked.set_serial(cert.get_serial_number())
        revoked.set_rev_date(datetime.datetime.utcnow().strftime("%y%m%d%H%M%SZ")) # ASN.1 format
        revoked.set_reason(reason)
        
        # Load current CRL
        crl = CA.load_crl()
        crl.add_revoked(revoked)
        
        # Do not double-revoke (zero logic)
        for r in crl.get_revoked():
            if r.get_serial() == cert.get_serial_number():
                return
        
        # Save CRL
        crl_path = f'{os.getenv("ROOT_DIR")}/{os.getenv("CRL")}'
        with open(crl_path, 'wb') as f:
            f.write(crypto.dump_crl(crypto.FILETYPE_PEM, crl))
    
    @staticmethod
    def load_crl() -> crypto.CRL:
        crl_path = f'{os.getenv("ROOT_DIR")}/{os.getenv("CRL")}'
        return crypto.load_crl(crypto.FILETYPE_PEM, crl_path)        