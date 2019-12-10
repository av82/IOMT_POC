# IOMT setup and test

IOMT: Index Ordered Merkle tree. The leaves of the tree contain circular linked leaves of the form index,next,value,level,position. Value can be any blob

## Requirements

python 3\
python sqlite

## High level details
The implementation is broken to persistence layer and interface layer. The persistence layer is performed by ```dbiomt.py```. 

**dbiomt.py:** provides persistence functions to store the iomt nodes/leaves in a database table as below with other helper functions

IOMT Table:
| indx  | next | value | level | position


Example Tabe:

| indx  | next | value | level | position
--- | --- | ---| --- | ---
10 | 20 | 'test'| 0 | 0
20 | 25 | 'test'| 0 | 1
40 | 5 | 'test'| 0 | 2
30 | 40 | 'test'| 0 | 3
5 | 10 | 'test'| 0 | 4
25 | 30 | 'test'| 0 | 5
None | None | None| 0 | 6
None | None | None| 0 | 7



**iomt.py:** provides iomt operations as below with other helper functions 
* `compute_leaf_hash`
* `compute_parent_hash`: This parent hash is slightly different, where if the `value` is `None` then the other value is returned. For example if left node value is `None` the right node value is returned as parent node hash
* `buildIOMT`
* `create_Add_Node_to_IOMT`: creates a new leaf and adds to IOMT
* `getProofVector_for_Node`: for a node/leaf provide the proof vector (this is only for one leaf/node but not multiple)

**IOMT organization**
* Level 0 is the level of leaves. 
* Level 1 is the first level of an IOMT, and hence the total number of levels is given as below
   ```
      adjusted_leaf_count=IOMT.nextPowerOf2(leaf_count)
      height=math.ceil(math.log2(adjusted_leaf_count))+1
   ```
* Each leaf defaults to index:None, next:None, value:None
* The level and position depends on the level of the current leaf/node, and current length of the nodes/leaves in that level. 
* If by adding a new leaf, the total number of leaves are not power of 2, we make it power of two by adding place-holder nodes. 
* For any new leaf that is to be added to the IOMT, check for existence of place-holder leaf in level 0, if there exists a place-holder leaf, the contents of place holder leaf are modified to new proposed leaf's contents.
* **Proof Vector**: Given a leaf or a node, the complementary leaves or nodes required to compute the root. The size of proof vector is log(height).
* **Proof Vector Verification**: Given known root, and Proof Vector, and a Leaf, verify if the Leaf is part of a known IOMT (if root obtained by building root with proof vector is equivalent to the known IOMT root).




