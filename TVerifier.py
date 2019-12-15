from hashlib import sha256

class TVerifier:
    def __init__(self,root_value):
        self.root_value = root_value
    
    def VerifyProofVector(self,proofvector):
        proof_length=len(proofvector)
        print('\nproof vector verification: ')
        for proof_elem in proofvector:
            print('height:',proof_elem[3],'position:',proof_elem[4],'hash:',proof_elem[2])
        hash_val=None
        if proof_length<1:
            return hash_val
        else:
            hash_val=proofvector[0][2]
            for i  in range(1,proof_length):
                temp_level=proofvector[i][3]+1
                temp_index=int(proofvector[i][4]/2)
                if proofvector[i][4]&1 == 1:
                    iomt_record=TVerifier.compute_parent_hash(hash_val,proofvector[i][2],temp_level,temp_index)
                    hash_val=iomt_record[0]
                else:
                    iomt_record=TVerifier.compute_parent_hash(proofvector[i][2],hash_val,temp_level,temp_index)
                    hash_val=iomt_record[0]
        print('proof root: ',hash_val,',original root',self.root_value,',verification result:',self.root_value==hash_val)
        return hash_val == self.root_value
        
    @staticmethod
    def compute_parent_hash(left_hash,right_hash,level,position):
        if left_hash=='0':
            return (right_hash,level,position)
        elif right_hash=='0':
            return (left_hash,level,position)
        else:
            return (str(sha256(str(left_hash).encode('utf-8')+str(right_hash).encode('utf-8')).hexdigest()),level,position)

    @staticmethod
    def compute_leaf_hash(leaf,level,position):
        if leaf[0] is None and leaf[1] is None and leaf[2] is None:   #return 0 for empty leaf
            return (0,level,position)
        else:
            return (sha256(str(leaf[0]).encode('utf-8')+str(leaf[2]).encode('utf-8')+str(leaf[1]).encode('utf-8')).hexdigest(),level,position)