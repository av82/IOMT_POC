from hashlib import sha256
import dbiomt 
from intervaltree import Interval, IntervalTree
import math

class Leaf:
    def __init__(self,index,next,value,level,position):
        self.index  =   index
        self.next   =   next
        self.value  =   value
        self.level  =   level # -1
        self.position =  position # incremental value
        
        
class Node:
    def __init__(self,level,position,value):
        self.hash = value
        self.level=level
        self.position=position

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
        #self.buildIOMT()
        
        
        #self.buildIOMT()
    def testwithNulls(self):
        leaf_value="test"
        self.create_Add_Leaf_to_IOMT(10,leaf_value)
        self.create_Add_Leaf_to_IOMT(20,leaf_value)
        self.create_Add_Leaf_to_IOMT(40,leaf_value)
        self.create_Add_Leaf_to_IOMT(30,leaf_value)
        self.buildIOMT()
        '''self.create_Add_Leaf_to_IOMT(5,leaf_value)
        self.create_Add_Leaf_to_IOMT(None,leaf_value)
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
        if leaf_count==0:
            iomt_leaf=(index,index,data,-1,0)
            self.iomtdb.create_iomt_record(conn,iomt_leaf)
            conn.commit()
            return
        if index is None:
            iomt_leaf=(None,None,None,-1,leaf_count)
            self.iomtdb.create_iomt_record(conn,iomt_leaf)
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
        
    def create_Add_Node_to_IOMT(self,level,data,position):
        conn = self.iomtdb.create_connection()
        iomt_node=(None,None,data,level,position)
        self.iomtdb.create_iomt_record(conn,iomt_node)
        return

    @staticmethod        
    def isPowerOfTwo(n): 
        if n==1:
             return True
        return (math.ceil(math.log2(n)) == math.floor(math.log2(n)))
    
    @staticmethod
    def nextPowerOf2(n): 
        if IOMT.isPowerOfTwo(n):
            return n
        p=1
        while (p < n) : 
            p <<= 1
        print('next power of 2:',p)
        return p 
        
    
    def buildIOMT(self):
        conn = self.iomtdb.create_connection()
        leaf_count=self.iomtdb.get_iomt_leaf_count(conn)
        adjusted_leaf_count=IOMT.nextPowerOf2(leaf_count)
        height=math.ceil(math.log2(IOMT.nextPowerOf2(leaf_count)))
        print('height',height)
        print('adjusted leaf count',adjusted_leaf_count)
        for i in range(1,height+1):
            self.IOMT.append(i)
            self.IOMT[i]=[]
        #populate empty leaves to meet power of two
        #TODO: optimize storage by not storing the empty leaves by using position.
        if not IOMT.isPowerOfTwo(leaf_count):
            for i in range(len(self.iomt_leaves),adjusted_leaf_count):
               self.create_Add_Leaf_to_IOMT(None,"test")

        for i in range(-1,height+1):
            if i==-1:
                for k in range(leaf_count):
                    iomt_record=self.iomtdb.get_min_place_holder_position(conn)
                    new_iomt_record=self.compute_leaf_hash(iomt_record,0,k)
                    self.create_Add_Node_to_IOMT(new_iomt_record[0],new_iomt_record[1],new_iomt_record[2])
            else:
                level_node_count=math.ceil(adjusted_leaf_count/i)
                lower_level_node_count=self.iomtdb.get_iomt_node_count_at_level(i-1)
                print('level node count',level_node_count)
                print('len of j',lower_level_node_count)
                for j in range(0,lower_level_node_count,2):
                    print('i',i,'j',j)
                    self.IOMT[i-1][j]
                    self.IOMT[i-1][j+1]
                    left=self.iomtdb.get_node_at(i-1,lower_level_node_count)
                    right=self.iomtdb.get_node_at(i-1,lower_level_node_count+1)
                    new_iomt_record=IOMT.compute_parent_hash(left,right,i,j)
                    self.create_Add_Node_to_IOMT(new_iomt_record[0],new_iomt_record[1],new_iomt_record[2])
        self.iomtdb.print_iomt_leaves(conn)
        self.root=self.IOMT[height][0]           
        return self.root
     
    @staticmethod
    def compute_parent_hash(left_node,right_node,level,position):
        if left_node.hash is 0:
            return (level,right_node[2],position)
        elif right_node.hash is 0:
            return Node(level,left_node[2],position)
        else:
             return Node(level,(sha256(str(left_node[2]).encode('utf-8')+str(right_node[2]).encode('utf-8')).hexdigest()),position)

    @staticmethod
    def compute_leaf_hash(leaf,position,level):
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
            iomtdb.create_iomt_record(conn,iomt_record_1)
            iomtdb.create_iomt_record(conn,iomt_record_2)
            iomtdb.create_iomt_record(conn,iomt_record_3)
            iomtdb.create_iomt_record(conn,iomt_record_4)
            iomtdb.select_iomt_leaf(conn,10)
    else:
        print("Error! cannot create the database connection.")'''
    IOMT(iomtdb)
  
if __name__== "__main__":
  main() 