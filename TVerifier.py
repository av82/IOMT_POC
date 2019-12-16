from hashlib import sha256

class TVerifier:
    def __init__(self,root_value=None):
        self.root_value = root_value
    
    #All operations are atomic
    def updateLeaf(self,leaf,proof_vector,current_root,new_root):
        return
    
    def updateTwoLeaves(self):
        return
    
    def updateThreeLeaves(self):
        return
    
    def verifyLeaf_for_Rules(self):
        return


    def VerifyProofVector(self,proofvector):
        proof_length=len(proofvector)
        print('\nproof vector verification: ')
        for proof_elem in proofvector:
            print('level:',proof_elem.level,'position:',proof_elem.position,'hash:',proof_elem.value)
        hash_val=None
        if proof_length<1:
            return hash_val
        else:
            hash_val=proofvector[0].value
            for i  in range(1,proof_length):
                temp_level=proofvector[i].level+1
                temp_index=int(proofvector[i].position/2)
                if proofvector[i].position &1 == 1:
                    iomt_record=self.compute_parent_hash(hash_val,proofvector[i].value,temp_level,temp_index)
                    hash_val=iomt_record[0]
                else:
                    iomt_record=self.compute_parent_hash(proofvector[i].value,hash_val,temp_level,temp_index)
                    hash_val=iomt_record[0]
        original_root=self.root_value
        print('proof root: ',hash_val,',original root',original_root,',verification result:',original_root==hash_val)
        return hash_val==original_root
        
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