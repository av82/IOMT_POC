from hashlib import sha256
import dbiomt 
import math
import random
import uuid
import testing.postgresql
from sqlalchemy import create_engine




class Node:
    def __init__(self,index,next,value,level,position):
        self.index = index
        self.next = next 
        self.value = value 
        self.level = level 
        self.position = position

class IOMT:
    '''
    Assumptions: index is unique identifier
    '''
    def __init__(self,iomtdb):
        self.root = None
        self.iomtdb = iomtdb
        self.testIOMT()
        #self.test()
        #self.setUp()
     
   
    ''' def setUp(self):
        pgsql = testing.postgresql.Postgresql()
        db = create_engine(pgsql.url())
        db.execute("CREATE TABLE longtest(id1 numeric, id2 numeric)")
        uuid.uuid4().int
        db.execute("INSERT INTO longtest values(%s,%s)",(uuid.uuid4().int,uuid.uuid4().int))
        result_set = db.execute("SELECT * FROM longtest")  
        for r in result_set:  
            a=r[0]
            b=r[1]
            print('a>b?',a==b)
            print(r)'''
   
    '''def test(self):
        conn = self.iomtdb.create_connection()
        sql = "insert into iomt values(%s,%s,%s,%s,%s)"
        conn.execute(sql,(uuid.uuid4().int,uuid.uuid4().int,"hash",1,0))'''
       

    def printProofVector(self,proof_leaf_test):
        print('proof vector for level: %d, position: %d' %(proof_leaf_test[0].level,proof_leaf_test[0].position))
        for proof_elem in proof_leaf_test:
            print('level:',proof_elem.level,',position:',proof_elem.position,',hash:',proof_elem.value)

    def printIOMT(self):
        conn = self.iomtdb.create_connection()
        print('\n-------PRINTING IOMT LEAVES------')
        self.iomtdb.print_iomt_leaves(conn)
        print('\n-------PRINTING IOMT NODES-------')
        self.iomtdb.print_iomt_nodes(conn)
        root=self.iomtdb.get_root(conn)
        if root is not None:
            print ('\n ROOT: ',root)
        min=self.iomtdb.get_min_iomt(conn)
        print('\nmin: ',min)
        max=self.iomtdb.get_max_iomt(conn)
        print('\nmax: ',max)
        
        #self.buildIOMT()
    def testIOMT(self):
        leaf_value="test"
        for i in range(12):
            index=uuid.uuid4().int
            self.create_Add_Leaf_to_IOMT(index,leaf_value)
            self.buildIOMT()
        
        '''
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
        self.buildIOMT()'''

        self.printIOMT()
        pv = self.getProofVector_for_Node(1,1)
        self.printProofVector(pv)
        pv = self.getProofVector_for_Node(7,1)
        self.printProofVector(pv)
        pv = self.getProofVector_for_Node(4,1)
        self.printProofVector(pv)
        p_vector=self.getProofVector_for_Node(1,1)
        self.VerifyProofVector(p_vector)
        p_vector=self.getProofVector_for_Node(7,1)
        self.VerifyProofVector(p_vector)
        p_vector=self.getProofVector_for_Node(4,1)
        self.VerifyProofVector(p_vector)
        (left_node_pos,right_node_pos,lr_level,common_parent,common_parent_level,v1,v2)=self.getCommonParent_Vector(4,7,1)
        self.printCommonParent_Vector(common_parent,common_parent_level,left_node_pos,right_node_pos,lr_level,v1,v2)
        (left_node_pos,right_node_pos,lr_level,common_parent,common_parent_level,v1,v2)=self.getCommonParent_Vector(0,1,1)
        self.printCommonParent_Vector(common_parent,common_parent_level,left_node_pos,right_node_pos,lr_level,v1,v2)
        pv=self.getVector_Three_Leaves(0,1,5)
        self.print_Three_Leaf_Proof_Vectors(pv[0],pv[1],pv[2],pv[3],pv[4],pv[5],pv[6],pv[7],pv[8])
    
    def print_Three_Leaf_Proof_Vectors(self,pair_left_leaf,pair_right_leaf,third_leaf,p_lv_to_cp,p_rv_to_cp,t_lv_to_cp_level,cp_lv_to_n_cp,cp_rv_to_n_cp,final_cp_v):
        print('\norder of applying compute_hash:',pair_left_leaf,pair_right_leaf,third_leaf)
        print('vector for left_leaf in pair: %d' %(pair_left_leaf))
        self.printProofVector(p_lv_to_cp)
        print('vector for right_leaf in pair: %d' %(pair_right_leaf))
        self.printProofVector(p_rv_to_cp)
        print('vector for third_leaf: %d' %(pair_right_leaf))
        self.printProofVector(t_lv_to_cp_level)
        print('\nvector for left of common parents:')
        self.printProofVector(cp_lv_to_n_cp)
        print('\vector for right of common parents:')
        self.printProofVector(cp_rv_to_n_cp)
        print('\nfinal vector from common parent of common parents to root:')
        self.printProofVector(final_cp_v)
        



    def printCommonParent_Vector(self,common_parent_pos,common_parent_level,pos_x,pos_y,level,v1,v2):
        print('\n-----Printing Common Parent node for',pos_x,pos_y,'at level:',level)
        if v1 is None and v2 is None:
            print('\nnodes are siblings, no common vector required ')
        else:
            print('\nproof vector for node 4 level 1:')
            for p in v1:
                print('l:',p.level,'p:',p.position)
            print('\nproof vector for node 7 level 1:')
            for p in v2:
                print('l:',p.level,'p:',p.position)
        print('\n common parent level:',common_parent_level,'common_parent position:',common_parent_pos)

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
        return
        
    def create_Add_Node_to_IOMT(self,data,level,position):
        conn = self.iomtdb.create_connection()
        iomt_node=(None,None,data,level,position)
        self.iomtdb.create_or_update_iomt_record(conn,iomt_node)
        conn.commit()
        return

    def getProofVector_for_Node(self,position,height,target_height=None):
        conn = self.iomtdb.create_connection()
        if target_height is None:
            target_height = self.iomtdb.get_max_level(conn)
        current_height = height
        current_position = position
        proof_vector=[]
        iomt_node = self.iomtdb.get_node_at(conn,current_height,current_position)
        node=Node(iomt_node[0],iomt_node[1],iomt_node[2],iomt_node[3],iomt_node[4])
        proof_vector.append(node)
        while(current_height<target_height):
            if current_position&1:
                current_position=current_position-1
            else:
                current_position=current_position+1
            iomt_node=self.iomtdb.get_node_at(conn,current_height,current_position)
            node=Node(iomt_node[0],iomt_node[1],iomt_node[2],iomt_node[3],iomt_node[4])
            proof_vector.append(node)
            current_height+=1
            current_position=int(current_position/2)
        return proof_vector
    
    def getCommonParent_Vector(self,node_pos_x, node_pos_y,height):
        if node_pos_x < node_pos_y:
            tmp_pos_x = node_pos_x
            tmp_pos_y = node_pos_y
        else:
            tmp_pos_x = node_pos_y
            tmp_pos_y = node_pos_x
        #proof vectors until common parent for x, y
        proof_vector_x_cp = []
        proof_vector_y_cp = []
        conn = self.iomtdb.create_connection()
        if (int)(tmp_pos_x>>1) == (int)(tmp_pos_y>>1):
            iomt_node_x=self.iomtdb.get_node_at(conn,height,tmp_pos_x)
            iomt_node_y=self.iomtdb.get_node_at(conn,height,tmp_pos_y)
            node_x=Node(iomt_node_x[0],iomt_node_x[1],iomt_node_x[2],iomt_node_x[3],iomt_node_x[4])
            node_y=Node(iomt_node_y[0],iomt_node_y[1],iomt_node_y[2],iomt_node_y[3],iomt_node_y[4])
            proof_vector_x_cp.append(node_x)
            proof_vector_y_cp.append(node_y)
            return (tmp_pos_x,tmp_pos_x,height,(int)(tmp_pos_x>>1),height+1,proof_vector_x_cp,proof_vector_y_cp) # just hash the nodes at height, posx, pos_y
        else:
            current_parent_height=height
            current_position_x=tmp_pos_x
            current_position_y=tmp_pos_y
            while (int)(current_position_x >> 1) != (int)(current_position_y >> 1):
                if current_position_x&1:
                    current_position_x=current_position_x-1
                else:
                    current_position_x=current_position_x+1
                if current_position_y&1:
                    current_position_y=current_position_y-1
                else:
                    current_position_y=current_position_y+1
                iomt_node_x=self.iomtdb.get_node_at(conn,current_parent_height,current_position_x)
                iomt_node_y=self.iomtdb.get_node_at(conn,current_parent_height,current_position_y)
                node_x=Node(iomt_node_x[0],iomt_node_x[1],iomt_node_x[2],iomt_node_x[3],iomt_node_x[4])
                node_y=Node(iomt_node_y[0],iomt_node_y[1],iomt_node_y[2],iomt_node_y[3],iomt_node_y[4])
                proof_vector_x_cp.append(node_x)
                proof_vector_y_cp.append(node_y)
                current_parent_height+=1
                current_position_x=int(current_position_x/2)
                current_position_y=int(current_position_y/2)

            return (tmp_pos_x,tmp_pos_y,height,(int)(current_position_x>>1),current_parent_height+1,proof_vector_x_cp,proof_vector_y_cp)
    
   
    def getVector_Three_Leaves(self,pos_x,pos_y,pos_z):
        '''
            re-ordered: (pair_left_leaf, pair_right_leaf, third_leaf
                        ,pair_left_vector_to_cp-1, pair_right_vector_to_cp-1
                        ,third_leaf_vector_to_cp_of_pair_left_leaf_and_pair_right_leaf
                        ,left_vector_from_common_parent_to_next_common_parent
                        ,right_vector_from_third_node_parent_at_common_parent_level_to_next_common_parent,
                        ,vector_from_final_common_parent_to_root)
                        
            
            left_leaf,right_leaf
            1. checks which 2 of 3 leaves should be combined first - gets common parent vector for those leaves
                output: [leaf_1_pos,leaf_2_pos,level=1,vector 1, vector2]
            2. gets the third leaf vector until the height of common parent of other two leaves obtained in (1)
                output: [leaf_3_pos,level=1,level=1,vector3]
            3. gets the common vector for the node at level from (2), and common parent from (1) to root.
                output: [node,level=1,level=1,vector3]
            output: [1,2,3]
        '''
        conn = self.iomtdb.create_connection()
        max_level=self.iomtdb.get_max_level(conn)
        print('\nThree node vector for : %d,%d,%d max_level:%d' %(pos_x,pos_y,pos_z,max_level))

        if pos_y < pos_x:
            IOMT.swap(pos_x, pos_y)
        if pos_z < pos_y:
            IOMT.swap(pos_z, pos_y)
        if pos_y < pos_x:
            IOMT.swap(pos_y, pos_x)
        pos_12 = pos_x ^ pos_y
        pos_23 = pos_z ^ pos_y
        i = IOMT.msb_position(pos_12)
        j = IOMT.msb_position(pos_23)
        pair_left_leaf,pair_right_leaf,third_leaf = pos_x,pos_y,pos_z
        p_lv_to_cp,p_rv_to_cp, t_lv_to_cp_level= [],[],[]
        cp_lv_to_n_cp,cp_rv_to_n_cp=[],[]
        final_cp_v = []
       
        if  i > j:
            pair_left_leaf,pair_right_leaf,third_leaf=pos_y,pos_z,pos_x  #first combine y,z
            (left_node_pos,right_node_pos,lr_level,common_parent_yz,common_parent_level_yz,v1,v2)=self.getCommonParent_Vector(pos_y,pos_z,1)
            print('common parent of %d,%d, of level %d,is %d, at level: %d' %(pos_y,pos_z,1,common_parent_yz,common_parent_level_yz))
            p_lv_to_cp  = v1
            p_rv_to_cp  = v2
            pvect_x_to_cp_yz=self.getProofVector_for_Node(pos_x,common_parent_level_yz)
            t_lv_to_cp_level = pvect_x_to_cp_yz
            x_v_pos=int(pvect_x_to_cp_yz[-1].position/2)
            
            (left_node_pos,right_node_pos,lr_level,common_parent_yz_x,common_parent_level_yz_x,v1,v2)=self.getCommonParent_Vector(x_v_pos,common_parent_yz,common_parent_level_yz)
            print('common parent of %d,%d,of level %d, is %d, at level: %d' %(x_v_pos,pos_z,common_parent_level_yz_x,common_parent_yz_x,common_parent_level_yz_x))
            cp_lv_to_n_cp = v1
            cp_rv_to_n_cp = v2
            if common_parent_level_yz_x < max_level:
                pvect_cp_to_root=self.getProofVector_for_Node(common_parent_yz_x,common_parent_level_yz_x)
                final_cp_v = pvect_cp_to_root
        else:
            pair_left_leaf,pair_right_leaf,third_leaf=pos_x,pos_y,pos_z  #first combine y,z
            (left_node_pos,right_node_pos,lr_level,common_parent_xy,common_parent_level_xy,v1,v2)=self.getCommonParent_Vector(pos_x,pos_y,1)
            print('common parent of %d,%d, of level %d, is %d, at level: %d' %(pos_x,pos_y,1,common_parent_xy,common_parent_level_xy))
            p_lv_to_cp  = v1
            p_rv_to_cp  = v2
            pvect_z_to_cp_xy=self.getProofVector_for_Node(pos_z,1,common_parent_level_xy)
            t_lv_to_cp_level = pvect_z_to_cp_xy
            z_v_pos=int(pvect_z_to_cp_xy[-1].position/2)
            
            (left_node_pos,right_node_pos,lr_level,common_parent_xy_z,common_parent_xy_z_level,v1,v2)=self.getCommonParent_Vector(z_v_pos,common_parent_xy,common_parent_level_xy)
            print('common parent of %d,%d, of level %d, is %d, at level: %d' %(z_v_pos,common_parent_xy,common_parent_level_xy,common_parent_xy,common_parent_xy_z_level))
            cp_lv_to_n_cp = v1
            cp_rv_to_n_cp = v2
            if common_parent_xy_z_level < max_level:
                    pvect_cp_to_root=self.getProofVector_for_Node(common_parent_xy_z,common_parent_xy_z_level)
                    final_cp_v = pvect_cp_to_root
        return (pair_left_leaf,pair_right_leaf,third_leaf,p_lv_to_cp,p_rv_to_cp,t_lv_to_cp_level,cp_lv_to_n_cp,cp_rv_to_n_cp,final_cp_v)
    
    def VerifyProofVector(self,proofvector):
        conn = self.iomtdb.create_connection()
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
        original_root=self.iomtdb.get_root(conn)
        print('proof root: ',hash_val,',original root',original_root,',verification result:',original_root==hash_val)
        return hash_val==original_root

    @staticmethod
    def swap(x, y):
        tmp = x
        x = y
        y = tmp
        return (x,y)
 
    @staticmethod
    def msb_position(n):
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
                    new_iomt_record=self.compute_leaf_hash(iomt_record,i,k)
                    self.create_Add_Node_to_IOMT(new_iomt_record[0],new_iomt_record[1],new_iomt_record[2])
            else:
                lower_level_node_count=self.iomtdb.get_iomt_node_count_at_level(conn,i-1)
                for j,l in zip(range(0,lower_level_node_count,2),range(0,math.ceil(lower_level_node_count/2))):
                    left=self.iomtdb.get_node_at(conn,i-1,j)
                    right=self.iomtdb.get_node_at(conn,i-1,j+1)
                    new_iomt_record=IOMT.compute_parent_hash(left[2],right[2],i,l)
                    self.create_Add_Node_to_IOMT(new_iomt_record[0],new_iomt_record[1],new_iomt_record[2])
        root=self.iomtdb.get_root(conn)
        self.root= root
        return self.root
     
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

   
def main():
    iomtdb=dbiomt.IOMT_DB()
    IOMT(iomtdb)
  
if __name__== "__main__":
  main() 