from hashlib import sha256
class Node:
    def __init__(self,index,next,value,level,position):
        self.index = index
        self.next = next 
        self.value = value 
        self.level = level 
        self.position = position

class TVerifier:
    def __init__(self,root_value):
        self.root_value = root_value
        print('Trusted Verifier Bootstrapped with Root:',root_value)
    
    @staticmethod
    def printProofVector(proof_leaf_test):
        print('proof vector for level: %d, position: %d' %(proof_leaf_test[0].level,proof_leaf_test[0].position))
        for proof_elem in proof_leaf_test:
            print('level:',proof_elem.level,',position:',proof_elem.position,',hash:',proof_elem.value)

    def check_leaf_integrity(self,leaf,hash):
        return self.compute_leaf_hash([leaf.index,leaf.next,leaf.value],leaf.position,leaf.level)[0]==hash
 
    #All operations are atomic
    def updateLeaf(self,leaf,proof_vector,current_root,new_root):

        return True
    
    def applyProofvector(self,proofvector):
        hash_val,temp_level,temp_position=proofvector[0].value,proofvector[0].level,proofvector[0].position
        for i  in range(1,len(proofvector)):
                temp_level=proofvector[i].level+1
                temp_position=int(proofvector[i].position/2)
                if proofvector[i].position &1 == 1:
                    iomt_record=self.compute_parent_hash(hash_val,proofvector[i].value,temp_level,temp_position)
                    hash_val=iomt_record[0]
                else:
                    iomt_record=self.compute_parent_hash(proofvector[i].value,hash_val,temp_level,temp_position)
                    hash_val=iomt_record[0]
        return Node(None,None,hash_val,temp_level,temp_position)

    def addLeaf(self,new_leaf,pv_new_leaf,old_leaf_1,pv_old_leaf_1,ol_cp_v1,nl_cp_v2,pv_cp_root,leaf_fit_case,current_root,new_root):
        '''
        except for first leaf of IOMT, adding a leaf will change
              1. if new_leaf index is < min of indexes -
                 new_leaf's next will be the the current minimum index of iomt.
                 ONE other older leaf has to be modified, that is current max, the next of current max has to be the new leaf.index
              2. if new_leaf index is > max of indexes 
                 new_leaf's next will be the the current minimum index of iomt.
                 ONE other leaf has to be modified, that is the current max, the next of current max has to be the new leaf.index
              3. if new_leaf index is between a leaf's index,next -   old_leaf_1.index < new_leaf < old_leaf_1.next
                 new_leaf's next will be the the old_leaf_1.next 
                 ONE other leaf has to be modified old_leaf_1.next is set to new_leaf.index
        '''
        old_leaf_1_check = False
        if new_leaf is None:
            return False
        if old_leaf_1 is not None:
            if self.check_leaf_integrity(old_leaf_1,pv_old_leaf_1[0].value):
                print('old_leaf verification inside TV:',old_leaf_1.position,old_leaf_1.value)
                #TVerifier.printProofVector(pv_old_leaf_1)
                self.VerifyProofVector(pv_old_leaf_1)
                old_leaf_1_check=True
            else:
                return False
        if old_leaf_1_check:
            # verify all logic of rules of system in verifyLeaf_for_Rules, only if it is TRUE, proceed to update tree
            if self.verifyLeaf_for_Rules(new_leaf) and self.verifyLeaf_for_Rules(old_leaf_1):
                if ol_cp_v1 is not None and nl_cp_v2 is not None:
                    cp_sibling_1=self.applyProofvector(ol_cp_v1)
                    cp_sibling_2=self.applyProofvector(nl_cp_v2)
                    left_sibling,right_sibling=None,None
                    if cp_sibling_1.position > cp_sibling_2.position:
                        left_sibling = cp_sibling_2
                        right_sibling = cp_sibling_1
                    else:
                        left_sibling = cp_sibling_1
                        right_sibling = cp_sibling_2
                    #print('sibling levels in TV')
                    #print(left_sibling.level,left_sibling.position,left_sibling.value)
                    #print(right_sibling.level,right_sibling.position,right_sibling.value)
                    first_cp=self.compute_parent_hash(left_sibling.value,right_sibling.value,left_sibling.level+1,(int)(left_sibling.position/2))
                    #print('first cp:',first_cp)
                    #check that the new proposed root is combination of the old leaf and new leaf, and simply not a random tree
                    if pv_cp_root is not None: 
                        TVerifier.printProofVector(pv_cp_root)
                        if first_cp[0] == pv_cp_root[0].value:
                            final_node = self.applyProofvector(pv_cp_root)
                            print('final computed root in TV:',final_node.value,'new proposed root:',new_root)
                            if final_node.value == new_root:
                                print('VERIFIED OLD LEAF with OLD ROOT', old_leaf_1.position)
                                print('VERIFIED OLD ROOT',self.root_value)
                                self.root_value = new_root #store new root only on all checks/computations, and sign it
                                print('UPDATED ROOT IN TRUSTED VERIFIER:',final_node.value)
                            else:
                                return False
                        else:
                            return False
            else:
                return False
        return True 

    def updateTwoLeaves(self):
        return
    
    def updateThreeLeaves(self):
        return
    
    def verifyLeaf_for_Rules(self,leaf):
        return True


    def VerifyProofVector(self,proofvector):
        proof_length=len(proofvector)
        print('\nproof vector verification inside Trusted Verifier: ')
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