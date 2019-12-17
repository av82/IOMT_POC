from hashlib import sha256
import dbiomt 
import math
import random
import uuid
import testing.postgresql
import TVerifier
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
        # below bootstrap is for test, it can be any random number, any content
        index=uuid.uuid4().int
        self.create_Add_Leaf_to_IOMT(index,"BOOTSTRAP")
        self.buildIOMT()
        self.printIOMT()
        #initialize Trusted verifier with a bootstrap root
        self.verifier = TVerifier.TVerifier(self.root)
        #test driver code to test IOMT
        self.testIOMT()
        #self.test()
        #self.setUp()
    
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
        conn = self.iomtdb.create_connection()
        for i in range(12):
            index=uuid.uuid4().int
            (affected_leaf,pv_affected_leaf,fit_case)=self.create_Add_Leaf_to_IOMT(index,leaf_value+str(i))
            #print('al:',affected_leaf.position,affected_leaf.value,affected_leaf.index,affected_leaf.next)
            #print('new_leaf index:',index)
            #self.printProofVector(pv_affected_leaf)
            #print('fit:',fit_case)

            old_root = self.root
            self.buildIOMT()
            new_root = self.root
            new_iomt_leaf = self.iomtdb.get_iomt_leaf_with_index(conn,index)
            new_leaf = Node(new_iomt_leaf[0],new_iomt_leaf[1],new_iomt_leaf[2],new_iomt_leaf[3],new_iomt_leaf[4])
            pv_new_leaf = self.getProofVector_for_Node(new_leaf.position,1)
            (left_node_pos,right_node_pos,lr_level,common_parent,common_parent_level,v1,v2) = self.getCommonParent_Vector(affected_leaf.position,new_leaf.position,1)
            #print('cp',common_parent,'cp level:',common_parent_level,'new leaf:',new_leaf.position,'old leaf:',affected_leaf.position,'total:',self.iomtdb.get_iomt_leaf_count(conn))
            pv_cp_to_root=self.getProofVector_for_Node(common_parent,common_parent_level)
            #print('new leaf:',new_leaf.position,'old leaf:',affected_leaf.position,'total:',self.iomtdb.get_iomt_leaf_count(conn))
            self.verifier.addLeaf(new_leaf,pv_new_leaf,affected_leaf,pv_affected_leaf,v1,v2,pv_cp_to_root,fit_case,old_root,new_root)
            
     
        
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
        #self.verifier.VerifyProofVector(p_vector)
        p_vector=self.getProofVector_for_Node(7,1)
        self.VerifyProofVector(p_vector)
        #self.verifier.VerifyProofVector(p_vector)
        p_vector=self.getProofVector_for_Node(4,1)
        self.VerifyProofVector(p_vector)
        #self.verifier.VerifyProofVector(p_vector)

        (left_node_pos,right_node_pos,lr_level,common_parent,common_parent_level,v1,v2)=self.getCommonParent_Vector(4,7,1)
        self.printCommonParent_Vector(common_parent,common_parent_level,left_node_pos,right_node_pos,lr_level,v1,v2)
        (left_node_pos,right_node_pos,lr_level,common_parent,common_parent_level,v1,v2)=self.getCommonParent_Vector(0,1,1)
        self.printCommonParent_Vector(common_parent,common_parent_level,left_node_pos,right_node_pos,lr_level,v1,v2)
        pv=self.getVector_Three_Leaves(0,1,5)
        self.print_Three_Leaf_Proof_Vectors(pv[0],pv[1],pv[2],pv[3],pv[4],pv[5],pv[6],pv[7],pv[8],pv[9])
        self.Verify_Three_Leaf_ProofVector(pv[0],pv[1],pv[2],pv[3],pv[4],pv[5],pv[6],pv[7],pv[8],pv[9])

        pv=self.getVector_Three_Leaves(0,4,5)
        self.print_Three_Leaf_Proof_Vectors(pv[0],pv[1],pv[2],pv[3],pv[4],pv[5],pv[6],pv[7],pv[8],pv[9])
        self.Verify_Three_Leaf_ProofVector(pv[0],pv[1],pv[2],pv[3],pv[4],pv[5],pv[6],pv[7],pv[8],pv[9])

    
    def check_leaf_integrity(self,leaf,hash):
        return self.compute_leaf_hash([leaf.index,leaf.next,leaf.value],leaf.position,leaf.level)[0]==hash
    
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
                
    def Verify_Three_Leaf_ProofVector(self,order,pair_left_leaf,pair_right_leaf,third_leaf,p_lv_to_cp,p_rv_to_cp,t_lv_to_cp_level,cp_lv_to_n_cp,cp_rv_to_n_cp,final_cp_v):
        print('\n------verification of three leafs to root-----')
        first_leaf_integrity = self.check_leaf_integrity(pair_left_leaf,p_lv_to_cp[0].value)
        second_leaf_integrity = self.check_leaf_integrity(pair_right_leaf,p_rv_to_cp[0].value)
        third_leaf_integrity = self.check_leaf_integrity(third_leaf,t_lv_to_cp_level[0].value)
        print('verify pair_left_leaf:',first_leaf_integrity)
        print('verify pair_right_leaf:',second_leaf_integrity)
        print('verify third_leaf:',third_leaf_integrity)
        if first_leaf_integrity == False or second_leaf_integrity == False or third_leaf_integrity == False:
            print('failed integrity check of leaves')
            return 
        cp_sibling_1=self.applyProofvector(p_lv_to_cp)
        cp_sibling_2=self.applyProofvector(p_rv_to_cp)
        left_sibling,right_sibling=None,None
        if cp_sibling_1.position > cp_sibling_2.position:
            left_sibling = cp_sibling_2
            right_sibling = cp_sibling_1
        else:
            left_sibling = cp_sibling_1
            right_sibling = cp_sibling_2
        print(left_sibling.level,left_sibling.position,left_sibling.value)
        print(right_sibling.level,right_sibling.position,right_sibling.value)
        first_cp=self.compute_parent_hash(left_sibling.value,right_sibling.value,left_sibling.level+1,(int)(left_sibling.position/2))
        print('first common parent of left,right pair of 3 leaves:')
        print(first_cp)
        tleaf_to_first_cp = self.applyProofvector(t_lv_to_cp_level)
        print('tleaf',tleaf_to_first_cp.level,tleaf_to_first_cp.position,tleaf_to_first_cp.value)
        self.printProofVector(cp_lv_to_n_cp)
        self.printProofVector(cp_rv_to_n_cp)
        print('checking tleaf')
        if tleaf_to_first_cp.value == cp_lv_to_n_cp[0].value or tleaf_to_first_cp.value == cp_rv_to_n_cp[0].value:
            print ('third leaf common parent checks out')
        else:
            print('failed check for third leaf to node at level of pairwise leaves and third leaf')
            return 
        cp_sibling_1=self.applyProofvector(cp_lv_to_n_cp)
        cp_sibling_2=self.applyProofvector(cp_rv_to_n_cp)
        left_sibling,right_sibling=None,None
        print('cp_sibling_1:',cp_sibling_1.level,cp_sibling_1.position)
        print('cp_sibling_2:',cp_sibling_2.level,cp_sibling_2.position)
        if cp_sibling_1.position > cp_sibling_2.position:
            left_sibling = cp_sibling_2
            right_sibling = cp_sibling_1
        else:
            left_sibling = cp_sibling_1
            right_sibling = cp_sibling_2
        print(left_sibling.level,left_sibling.position,left_sibling.value)
        print(right_sibling.level,right_sibling.position,right_sibling.value)
        last_cp=self.compute_parent_hash(left_sibling.value,right_sibling.value,left_sibling.level+1,(int)(left_sibling.position/2))
        print('first highest common parent of left,right pair of 3 leaves:')
        print(last_cp)
        final_check=False
        if last_cp[0] != final_cp_v[0].value:
            final_check = False
        else:
            final_node = self.applyProofvector(final_cp_v)
            if final_node is not None and final_node.value==self.root:
                print('success')
                final_check = True
                print('final hash from applying final proof vector:',final_node.value)
        return final_check
    
    def Verify_Two_Leaf_ProofVector(self,pair_left_leaf,pair_right_leaf,third_leaf,p_lv_to_cp,p_rv_to_cp,t_lv_to_cp_level,cp_lv_to_n_cp,cp_rv_to_n_cp,final_cp_v):

        return

    def print_Three_Leaf_Proof_Vectors(self,order,pair_left_leaf,pair_right_leaf,third_leaf,p_lv_to_cp,p_rv_to_cp,t_lv_to_cp_level,cp_lv_to_n_cp,cp_rv_to_n_cp,final_cp_v):
        print('\norder of applying compute_hash:',pair_left_leaf.position,pair_right_leaf.position,third_leaf.position)
        print('vector for left_leaf in pair: %d' %(pair_left_leaf.position))
        self.printProofVector(p_lv_to_cp)
        print('vector for right_leaf in pair: %d' %(pair_right_leaf.position))
        self.printProofVector(p_rv_to_cp)
        print('vector for third_leaf: %d' %(third_leaf.position))
        self.printProofVector(t_lv_to_cp_level)
        print('\nvector for left of common parents:')
        self.printProofVector(cp_lv_to_n_cp)
        print('\nvector for right of common parents:')
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
        conn = self.iomtdb.create_connection()
        leaf_count=self.iomtdb.get_iomt_leaf_count(conn)
        affected_old_leaf,aol_proof_vector = None,[]
        case=-1
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
            case = 1
            new_max=index
            max_leaf=self.iomtdb.get_max_index_leaf(conn)
            affected_old_leaf = Node(max_leaf[0],max_leaf[1],max_leaf[2],max_leaf[3],max_leaf[4])
            aol_proof_vector=self.getProofVector_for_Node(affected_old_leaf.position,1)
            self.iomtdb.set_max_indx_iomt(conn,new_max,data)
        elif index<min:
            case = 2
            new_min=index
            min_leaf=self.iomtdb.get_min_index_leaf(conn)
            affected_old_leaf = Node(min_leaf[0],min_leaf[1],min_leaf[2],min_leaf[3],min_leaf[4])
            aol_proof_vector = self.getProofVector_for_Node(affected_old_leaf.position,1)
            self.iomtdb.set_min_indx_iomt(conn,new_min,data)
        else:
            case = 3
            range=self.iomtdb.check_enclosure(conn,index) 
            if range is not None:
                 encloser_leaf = self.iomtdb.get_iomt_leaf_at_pos(conn,range[2])
                 if encloser_leaf is not None:
                    affected_old_leaf = Node(encloser_leaf[0],encloser_leaf[1],encloser_leaf[2],encloser_leaf[3],encloser_leaf[4])
                    aol_proof_vector = self.getProofVector_for_Node(affected_old_leaf.position,1)
                    self.iomtdb.split_interval_iomt(conn,index,range[0],data)
        conn.commit()
        return (affected_old_leaf,aol_proof_vector,case)
        
    def create_Add_Node_to_IOMT(self,data,level,position):
        conn = self.iomtdb.create_connection()
        iomt_node=(None,None,data,level,position)
        self.iomtdb.create_or_update_iomt_record(conn,iomt_node)
        conn.commit()
        return

    def getProofVector_for_Node(self,position,level,target_height=None):
        conn = self.iomtdb.create_connection()
        if target_height is None:
            target_height = self.iomtdb.get_max_level(conn)
        current_height = level
        current_position = position
        proof_vector=[]
        iomt_node = self.iomtdb.get_node_at(conn,current_height,current_position)
        #print('iomt_node',iomt_node,'level:',current_height,'position:',position)
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
        #print ('tmp_pos_x:',tmp_pos_x,'tmp_pos_y:',tmp_pos_y)
        #proof vectors until common parent for x, y
        proof_vector_x_cp = []
        proof_vector_y_cp = []
        conn = self.iomtdb.create_connection()
        iomt_node_x=self.iomtdb.get_node_at(conn,height,tmp_pos_x)
        iomt_node_y=self.iomtdb.get_node_at(conn,height,tmp_pos_y)
        node_x=Node(iomt_node_x[0],iomt_node_x[1],iomt_node_x[2],iomt_node_x[3],iomt_node_x[4])
        node_y=Node(iomt_node_y[0],iomt_node_y[1],iomt_node_y[2],iomt_node_y[3],iomt_node_y[4])
        proof_vector_x_cp.append(node_x)
        proof_vector_y_cp.append(node_y)
        if (int)(tmp_pos_x>>1) == (int)(tmp_pos_y>>1):
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
        order = None
        if  i > j:
            order = 0
            pair_left_leaf,pair_right_leaf,third_leaf=pos_y,pos_z,pos_x  #first combine y,z
            (left_node_pos,right_node_pos,lr_level,common_parent_yz,common_parent_level_yz,v1,v2)=self.getCommonParent_Vector(pos_y,pos_z,1)
            print('common parent of %d,%d, of level %d,is at position: %d, at level: %d' %(pos_y,pos_z,1,common_parent_yz,common_parent_level_yz))
            p_lv_to_cp  = v1
            p_rv_to_cp  = v2
            pvect_x_to_cp_yz=self.getProofVector_for_Node(pos_x,1,common_parent_level_yz)
            t_lv_to_cp_level = pvect_x_to_cp_yz
            x_v_pos=int(pvect_x_to_cp_yz[-1].position/2)
            (left_node_pos,right_node_pos,lr_level,common_parent_yz_x,common_parent_level_yz_x,v1,v2)=self.getCommonParent_Vector(x_v_pos,common_parent_yz,common_parent_level_yz)
            print('common parent of %d,%d,of level %d, is at position: %d, at level: %d' %(x_v_pos,common_parent_yz,common_parent_level_yz,common_parent_yz_x,common_parent_level_yz_x))
            cp_lv_to_n_cp = v1
            cp_rv_to_n_cp = v2
            if common_parent_level_yz_x < max_level:
                pvect_cp_to_root=self.getProofVector_for_Node(common_parent_yz_x,common_parent_level_yz_x)
                final_cp_v = pvect_cp_to_root
        else:
            order = 1 
            pair_left_leaf,pair_right_leaf,third_leaf=pos_x,pos_y,pos_z  #first combine y,z
            (left_node_pos,right_node_pos,lr_level,common_parent_xy,common_parent_level_xy,v1,v2)=self.getCommonParent_Vector(pos_x,pos_y,1)
            print('common parent of %d,%d, of level %d, is at position: %d, at level: %d' %(pos_x,pos_y,1,common_parent_xy,common_parent_level_xy))
            p_lv_to_cp  = v1
            p_rv_to_cp  = v2
            pvect_z_to_cp_xy=self.getProofVector_for_Node(pos_z,1,common_parent_level_xy)
            t_lv_to_cp_level = pvect_z_to_cp_xy
            z_v_pos=int(pvect_z_to_cp_xy[-1].position/2)
            
            (left_node_pos,right_node_pos,lr_level,common_parent_xy_z,common_parent_xy_z_level,v1,v2)=self.getCommonParent_Vector(z_v_pos,common_parent_xy,common_parent_level_xy)
            print('common parent of %d,%d, of level %d, is at position: %d, at level: %d' %(z_v_pos,common_parent_xy,common_parent_level_xy,common_parent_xy,common_parent_xy_z_level))
            cp_lv_to_n_cp = v1
            cp_rv_to_n_cp = v2
            if common_parent_xy_z_level < max_level:
                pvect_cp_to_root=self.getProofVector_for_Node(common_parent_xy_z,common_parent_xy_z_level)
                final_cp_v = pvect_cp_to_root
        iomt_node=self.iomtdb.get_iomt_leaf_at_pos(conn,pair_left_leaf)
        pair_left_leaf=Node(iomt_node[0],iomt_node[1],iomt_node[2],iomt_node[3],iomt_node[4])
        iomt_node=self.iomtdb.get_iomt_leaf_at_pos(conn,pair_right_leaf)
        pair_right_leaf=Node(iomt_node[0],iomt_node[1],iomt_node[2],iomt_node[3],iomt_node[4])
        iomt_node=self.iomtdb.get_iomt_leaf_at_pos(conn,third_leaf)
        third_leaf=Node(iomt_node[0],iomt_node[1],iomt_node[2],iomt_node[3],iomt_node[4])
            
        return (order,pair_left_leaf,pair_right_leaf,third_leaf,p_lv_to_cp,p_rv_to_cp,t_lv_to_cp_level,cp_lv_to_n_cp,cp_rv_to_n_cp,final_cp_v)
    
    def VerifyProofVector(self,proofvector):
        conn = self.iomtdb.create_connection()
        proof_length=len(proofvector)
        print('\nproof vector verification inside Untrusted Prover: ')
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
               self.create_Add_Leaf_to_IOMT(None,"test"+str(i))
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