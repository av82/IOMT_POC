from hashlib import sha256
import dbiomt 
from intervaltree import Interval, IntervalTree
import math

'''
    Assumptions: index is unique identifier
'''
class IOMT:
    def __init__(self,iomtdb):
        self.IOMT=[[]]
        self.iomt_leaves=[]
        self.levels=None
        self.root=None
        self.iomtdb=iomtdb
        self.testwithNulls()
        self.printIOMT()
        self.printProofVector(1,1)
        self.printProofVector(7,1)
        self.printProofVector(4,1)
        p_vector=self.getProofVector_for_Node(1,1)
        self.VerifyProofVector(p_vector)
        p_vector=self.getProofVector_for_Node(7,1)
        self.VerifyProofVector(p_vector)
        p_vector=self.getProofVector_for_Node(4,1)
        self.VerifyProofVector(p_vector)
      
    
    def VerifyProofVector(self,proofvector):
        conn = self.iomtdb.create_connection()
        proof_length=len(proofvector)
        print('\nproof vector verification: ')
        for proof_elem in proofvector:
            print('height:',proof_elem[3],'index:',proof_elem[4],'hash:',proof_elem[2])
        hash_val=None
        if proof_length<1:
            return hash_val
        else:
            hash_val=proofvector[0][2]
            for i  in range(1,proof_length):
                temp_level=proofvector[i][3]+1
                temp_index=int(proofvector[i][4]/2)
                if proofvector[i][4]&1 == 1:
                    iomt_record=self.compute_parent_hash(hash_val,proofvector[i][2],temp_level,temp_index)
                    hash_val=iomt_record[0]
                else:
                    iomt_record=self.compute_parent_hash(proofvector[i][2],hash_val,temp_level,temp_index)
                    hash_val=iomt_record[0]
        original_root=self.iomtdb.get_root(conn)
        print('proof root: ',hash_val,',original root',original_root,',verification result:',original_root==hash_val)
        return hash_val==original_root

    def printProofVector(self,index,height):
        proof_leaf_test=self.getProofVector_for_Node(index,height)
        print('\nproof vector for leaf: ',index)
        for proof_elem in proof_leaf_test:
            print('height:',proof_elem[3],'index:',proof_elem[4],'hash:',proof_elem[2])

    def printIOMT(self):
        conn = self.iomtdb.create_connection()
        print('\n-------PRINTING IOMT LEAVES------')
        self.iomtdb.print_iomt_leaves(conn)
        print('\n-------PRINTING IOMT NODES-------')
        self.iomtdb.print_iomt_nodes(conn)
        root=self.iomtdb.get_root(conn)
        if root is not None:
            print ('\n ROOT: ',root)
        
        
        
        #self.buildIOMT()
    def testwithNulls(self):
        leaf_value="test"
        self.create_Add_Leaf_to_IOMT(10,leaf_value)
        self.buildIOMT()
        self.create_Add_Leaf_to_IOMT(20,leaf_value)
        self.buildIOMT()
        self.create_Add_Leaf_to_IOMT(40,leaf_value)
        self.buildIOMT()
        self.create_Add_Leaf_to_IOMT(30,leaf_value)
        self.buildIOMT()
        #new min case
        self.create_Add_Leaf_to_IOMT(5,leaf_value)
        self.buildIOMT()
        #new enclosure case
        self.create_Add_Leaf_to_IOMT(25,leaf_value)
        self.buildIOMT()

        #conn = self.iomtdb.create_connection()
        #self.iomtdb.print_iomt_leaves(conn)
        
        #self.iomtdb.print_iomt_leaves(conn)
        #self.create_Add_Leaf_to_IOMT(5,leaf_value)
        #self.buildIOMT()
        '''self.create_Add_Leaf_to_IOMT(None,leaf_value)
        self.create_Add_Leaf_to_IOMT(25,leaf_value)
        self.create_Add_Leaf_to_IOMT(2,leaf_value)
        self.create_Add_Leaf_to_IOMT(None,leaf_value)
        self.create_Add_Leaf_to_IOMT(45,leaf_value)
        conn = self.iomtdb.create_connection()
        self.iomtdb.print_iomt_leaves(conn)'''
    
    '''
        create new iomt leaf
    '''
    def create_Add_Leaf_to_IOMT(self,index,data):
        conn = self.iomtdb.create_connection()
        leaf_count=self.iomtdb.get_iomt_leaf_count(conn)
        #print('leaf_count',leaf_count,'index:',index)
        if leaf_count==0:
            iomt_leaf=(index,index,data,0,0)
            self.iomtdb.create_or_update_iomt_record(conn,iomt_leaf)
            conn.commit()
            return
        if index is None:
            iomt_leaf=(None,None,None,0,leaf_count)
            self.iomtdb.create_or_update_iomt_record(conn,iomt_leaf)
            conn.commit()
            return
        min=self.iomtdb.get_min_iomt(conn)
        max=self.iomtdb.get_max_iomt(conn)
        conn = self.iomtdb.create_connection()
        if index>max:
            new_max=index
            self.iomtdb.set_max_indx_iomt(conn,new_max,data)
        elif index<min:
            new_min=index
            self.iomtdb.set_min_indx_iomt(conn,new_min,data)
        else:
             range=self.iomtdb.check_enclosure(conn,index) 
             if range is not None:
                 self.iomtdb.split_interval_iomt(conn,index,range[0],data)
        conn.commit()
        #self.iomtdb.get_iomt_leaf_with_index(conn,index)
        return
        
    def create_Add_Node_to_IOMT(self,data,level,position):
        conn = self.iomtdb.create_connection()
        iomt_node=(None,None,data,level,position)
        #print('create_node',iomt_node)
        self.iomtdb.create_or_update_iomt_record(conn,iomt_node)
        conn.commit()
        return

    def getProofVector_for_Node(self,position,height):
        conn = self.iomtdb.create_connection()
        max_height = self.iomtdb.get_max_level(conn)
        current_height=height
        current_position=position
        leaf_proof_vector=[]
        iomt_node=self.iomtdb.get_node_at(conn,current_height,current_position)
        leaf_proof_vector.append(iomt_node)
        while(current_height<max_height):
            if current_position&1:
                current_position=current_position-1
            else:
                current_position=current_position+1
            iomt_node=self.iomtdb.get_node_at(conn,current_height,current_position)
            leaf_proof_vector.append(iomt_node)
            current_height+=1
            current_position=int(current_position/2)
        return leaf_proof_vector

        
    @staticmethod
    def msb(n):
        return int(math.log(n,2))

    @staticmethod        
    def isPowerOfTwo(n): 
        if n==1:
             return True
        return (n & (n-1) == 0) and n != 0
    
    @staticmethod
    def nextPowerOf2(n): 
        if IOMT.isPowerOfTwo(n):
            return n
        p=1
        while (p < n) : 
            p <<= 1
        #print('next power of 2:',p)
        return p 
        
    '''
      TODO: // optimize by providing proof vectors for updates etc.
    '''
    def buildIOMT(self):
        conn = self.iomtdb.create_connection()
        leaf_count=self.iomtdb.get_iomt_leaf_count(conn)
        adjusted_leaf_count=IOMT.nextPowerOf2(leaf_count)
        height=math.ceil(math.log2(adjusted_leaf_count))+1
        #print('height of the tree:',height)
        #print('adjusted leaf count',adjusted_leaf_count)
        #print('iomt height',height)
       
        #populate empty leaves to meet power of two
        #TODO: optimize storage by not storing the empty leaves by using position.
        if not IOMT.isPowerOfTwo(leaf_count):
            for i in range(leaf_count,adjusted_leaf_count):
               self.create_Add_Leaf_to_IOMT(None,"test")
               conn.commit()
        #self.iomtdb.print_iomt_leaves(conn)

        for i in range(1,height+1):
            if i==1:
                for k in range(0,adjusted_leaf_count):
                    iomt_record=self.iomtdb.get_iomt_leaf_at_pos(conn,k)
                    #print(iomt_record)
                    new_iomt_record=self.compute_leaf_hash(iomt_record,i,k)
                    #print('new_iomt_record',new_iomt_record)
                    self.create_Add_Node_to_IOMT(new_iomt_record[0],new_iomt_record[1],new_iomt_record[2])
                #self.iomtdb.print_iomt_leaves(conn)
                #self.iomtdb.print_iomt_nodes(conn)
            else:
                #level_node_count= math.ceil(adjusted_leaf_count/i) 
                lower_level_node_count=self.iomtdb.get_iomt_node_count_at_level(conn,i-1)
                #print('lower_level_node_count',i-1,lower_level_node_count)
                #print('level node count',level_node_count)
                #print('len of j',lower_level_node_count)
                for j,l in zip(range(0,lower_level_node_count,2),range(0,math.ceil(lower_level_node_count/2))):
                    #print('i',i,'j',j)
                    #self.iomtdb.print_iomt_nodes(conn)
                    left=self.iomtdb.get_node_at(conn,i-1,j)
                    right=self.iomtdb.get_node_at(conn,i-1,j+1)
                    new_iomt_record=IOMT.compute_parent_hash(left[2],right[2],i,l)
                    #print('new_iomt_record',new_iomt_record)
                    self.create_Add_Node_to_IOMT(new_iomt_record[0],new_iomt_record[1],new_iomt_record[2])
        root=self.iomtdb.get_root(conn)
        self.root= root
        return self.root
     
    @staticmethod
    def compute_parent_hash(left_hash,right_hash,level,position):
        #print('l:',left_hash,'r:',right_hash,'h:',level,'p:',position)
        if left_hash=='0':
            return (right_hash,level,position)
        elif right_hash=='0':
            return (left_hash,level,position)
        else:
             return (str(sha256(str(left_hash).encode('utf-8')+str(right_hash).encode('utf-8')).hexdigest()),level,position)

    @staticmethod
    def compute_leaf_hash(leaf,level,position):
        #print('level:',level,'pos:',position)
        if leaf[0] is None and leaf[1] is None and leaf[2] is None:   #return 0 for empty leaf
            return (0,level,position)
        else:
            return (sha256(str(leaf[0]).encode('utf-8')+str(leaf[2]).encode('utf-8')+str(leaf[1]).encode('utf-8')).hexdigest(),level,position)

   
def main():
    iomtdb=dbiomt.IOMT_DB('iomt.db')
    IOMT(iomtdb)
  
if __name__== "__main__":
  main() 