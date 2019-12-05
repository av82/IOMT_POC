from hashlib import sha256
from intervaltree import Interval, IntervalTree
import math

class Leaf:
    def __init__(self,index,next,value):
        self.index  =   index
        self.next   =   next
        self.value  =   value
        
class Node:
    def __init__(self,hash):
        self.hash = hash

'''
    Assumptions: index is unique identifier
'''
class IOMT:
    def __init__(self):
        self.IOMT=[[]]
        self.iomt_leaves=[]
        self.levels=None
        self.root=None
        self.interval_tree= IntervalTree() # this can be maintained outside IOMT in a database. but for now leaving here
        # let's call i,None a special leaf for poc purposes, as interval_trees lib does not allow null intervals, but allows unbound interval
        leaf_value="test"
        #init interval tree
        init_interval=Interval(-10,10,0) # special leaf - first leaf, index, next are actually supposed to be the same, interval tree does not support it yet
        self.interval_tree.add(init_interval)
        new_leaf=Leaf(-10,10,leaf_value) # this is because interval tree does not support identity interval <i,i>
        self.iomt_leaves.append(new_leaf)
        #print(self.interval_tree)
        #create first leaf -- in a database model we would not choose a None as next index of first leaf, it should be <index,index>
        self.create_AddLeaf_to_IOMT(20,leaf_value)
        self.create_AddLeaf_to_IOMT(30,leaf_value)
        self.create_AddLeaf_to_IOMT(40,leaf_value)
        #self.create_AddLeaf_to_IOMT(50,leaf_value)
        self.buildIOMT()
    '''
     inputs: Index, data
     output: new Leaf is created and added iomt - added to interval tree, appended to merkle leaves array 
    '''
    def create_AddLeaf_to_IOMT(self,index,data):
        merkle_pos=len(self.iomt_leaves) # the future position of the leaf in the IOMT
        prep_leaf=self.prepareLeaf(index,merkle_pos)
        #print('prepleaf',prep_leaf)
        new_leaf=Leaf(prep_leaf[0][0],prep_leaf[0][1],data) # this is because interval tree does not support identity interval <i,i>
        self.iomt_leaves.append(new_leaf) # since there is no support for circular interval in interval_tree , we need to track it in merkle array
      
    '''
    inputs: leaf, merkle_pos: count of this potential position of the leaf in merkle tree
    output: the leaf inserted into the interval_tree due to one of below:
        1.  slice of an existing leaf(interval)
        2.  prepend to begin of interval tree
        3.  appending to end of interval tree
        note: not handling coverage of equals, handling only greater or less than, as assumption is identifiers are unique
            : if we want to support null intervals like (0,0) or (20,0), we need to overwrite this interval tree rules somewhere.
    '''
    def prepareLeaf(self,index,merkle_pos):
        #check if there is an overlapping index, i.e: membership of some existing range, 
        #else check if less than min, greater than max 
        end=self.interval_tree.end()
        begin=self.interval_tree.begin()
        #print('begin,end',begin,end)
        returnval=None
        if self.interval_tree.overlaps(index):
            self.interval_tree.slice(index)
            returnval=self.interval_tree.at(index)
        elif index>self.interval_tree.end():
            self.interval_tree.addi(end,index,merkle_pos)
            returnval=self.interval_tree.at(index-1)
        elif index<self.interval_tree.begin():
            self.interval_tree.addi(index,begin,merkle_pos)
            returnval=self.interval_tree.at(index)
        #print('int_tree',list((returnval)))
        return list(returnval)
    
    @staticmethod        
    def isPowerOfTwo(n): 
        if n==1:
             return True
        return (math.ceil(math.log2(n)) == math.floor(math.log2(n)))
    
    @staticmethod
    def nextPowerOf2(n): 
        if IOMT.isPowerOfTwo(n):
            return n
        p=0
        while (p < n) : 
            p <<= 1
        print('next power of 2:',p)
        return p 
    
    def buildIOMT(self):
        leaf_count=len(self.iomt_leaves)
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
                new_leaf=Leaf(None,None,None)
                self.iomt_leaves.append(new_leaf)

        for i in range(0,height+1):
            if i==0:
                for k in range(len(self.iomt_leaves)):
                    node=IOMT.compute_leaf_hash(self.iomt_leaves[k])
                    self.IOMT[i].append(node)
            else:
                level_node_count=math.ceil(adjusted_leaf_count/i)
                print('level node count',level_node_count)
                print('len of j',len(self.IOMT[i-1]))
                for j in range(0,len(self.IOMT[i-1]),2):
                    print('i',i,'j',j)
                    node=IOMT.compute_parent_hash(self.IOMT[i-1][j],self.IOMT[i-1][j+1])
                    self.IOMT[i].append(node)
        for i in range(len(self.IOMT)):
            for j in range(len(self.IOMT[i])):
                print('level:',i,'node:',j,',',self.IOMT[i][j].hash)
        print(self.interval_tree)
        self.root=self.IOMT[height][0]           
        return self.root
     
    @staticmethod
    def compute_parent_hash(left_node,right_node):
        if left_node.hash is 0:
            return right_node
        elif right_node.hash is 0:
            return left_node
        else:
             return Node((sha256(str(left_node.hash).encode('utf-8')+str(right_node.hash).encode('utf-8')).hexdigest()))

    @staticmethod
    def compute_leaf_hash(leaf):
        if leaf.index is None and leaf.next is None and leaf.data is None:   #return 0 for empty leaf
            return Node(0)
        else:
            return Node(((sha256(str(leaf.index).encode('utf-8')+str(leaf.value).encode('utf-8')+str(leaf.next).encode('utf-8')).hexdigest())))

   
def main():
    IOMT()
  
if __name__== "__main__":
  main() 