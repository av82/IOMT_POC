from hashlib import sha256
import dbiomt 
from intervaltree import Interval, IntervalTree
import math

class Leaf_ProofVector:
    def __init__(self,level,index):
        self.level=level
        self.index=index

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
        self.printProofVector(1)
        self.printProofVector(7)
        self.printProofVector(4)

        
    
    def printProofVector(self,index):
        proof_leaf_test=self.getProofVector_for_Leaf(index)
        print('\nproof vector for leaf: ',index)
        for proof_elem in proof_leaf_test:
            print('height:',proof_elem.level,'index:',proof_elem.index)

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

    def getProofVector_for_Node(self,level,index):
        return
   
    def getProofVector_for_Leaf(self,index):
        conn = self.iomtdb.create_connection()
        max_height = self.iomtdb.get_max_level(conn)
        current_height=0
        current_index=index
        leaf_proof_vector=[]
        while(current_height<max_height):
            if current_index&1:
                current_index=current_index-1
            else:
                current_index=current_index+1
            vector_element=Leaf_ProofVector(current_height,current_index)
            leaf_proof_vector.append(vector_element)
            current_height+=1
            current_index=int(current_index/2)
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
        print('next power of 2:',p)
        return p 
        
    '''
      TODO: // optimize by providing proof vectors for updates etc.
    '''
    def buildIOMT(self):
        conn = self.iomtdb.create_connection()
        leaf_count=self.iomtdb.get_iomt_leaf_count(conn)
        first_level_node_count=self.iomtdb.get_iomt_node_count_at_level(conn,1)
        adjusted_leaf_count=IOMT.nextPowerOf2(leaf_count)
        height=math.ceil(math.log2(IOMT.nextPowerOf2(leaf_count)))+1
        #print('adjusted leaf count',adjusted_leaf_count)
        #print('iomt height',height)
       
        #populate empty leaves to meet power of two
        #TODO: optimize storage by not storing the empty leaves by using position.
        if not IOMT.isPowerOfTwo(leaf_count):
            for i in range(leaf_count,adjusted_leaf_count):
               self.create_Add_Leaf_to_IOMT(None,"test")
               conn.commit()
        #self.iomtdb.print_iomt_leaves(conn)

        for i in range(1,height):
            if i==1:
                for k in range(0,adjusted_leaf_count):
                    iomt_record=self.iomtdb.get_iomt_leaf_at_pos(conn,k)
                    print(iomt_record)
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
                    new_iomt_record=IOMT.compute_parent_hash(left,right,i,l)
                    #print('new_iomt_record',new_iomt_record)
                    self.create_Add_Node_to_IOMT(new_iomt_record[0],new_iomt_record[1],new_iomt_record[2])
        root=self.iomtdb.get_root(conn)
        self.root= root
        return self.root
     
    @staticmethod
    def compute_parent_hash(left_node,right_node,level,position):
        #print('left',left_node[2],left_node[2]=='0','right',right_node[2],right_node[2]=='0')
        if left_node[2]=='0':
            return (right_node[2],level,position)
        elif right_node[2]=='0':
            return (left_node[2],level,position)
        else:
             return (sha256(str(left_node[2]).encode('utf-8')+str(right_node[2]).encode('utf-8')).hexdigest(),level,position)

    @staticmethod
    def compute_leaf_hash(leaf,level,position):
        print('level:',level,'pos:',position)
        if leaf[0] is None and leaf[1] is None and leaf[2] is None:   #return 0 for empty leaf
            return (0,level,position)
        else:
            return (sha256(str(leaf[0]).encode('utf-8')+str(leaf[2]).encode('utf-8')+str(leaf[1]).encode('utf-8')).hexdigest(),level,position)

   
def main():
    iomtdb=dbiomt.IOMT_DB('iomt.db')
    conn = iomtdb.create_connection()
    # create tables
    '''if conn is not None:
        # create projects table
        with conn:
            iomt_record_1=(-10,10,'test',0,0)
            iomt_record_2=(10,20,'test',0,1)
            iomt_record_3=(20,30,'test',0,2)
            iomt_record_4=(30,40,'test',0,3)
            iomtdb.create_or_update_iomt_record(conn,iomt_record_1)
            iomtdb.create_or_update_iomt_record(conn,iomt_record_2)
            iomtdb.create_or_update_iomt_record(conn,iomt_record_3)
            iomtdb.create_or_update_iomt_record(conn,iomt_record_4)
            iomtdb.select_iomt_leaf(conn,10)
    else:
        print("Error! cannot create the database connection.")'''
    IOMT(iomtdb)
  
if __name__== "__main__":
  main() 