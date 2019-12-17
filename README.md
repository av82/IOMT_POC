# IOMT setup and test

IOMT: Index Ordered Merkle tree. The leaves of the tree contain circular linked leaves of the form index,next,value,level,position. Value can be any blob.

* This datastructure is useful in following avenues:
    * where an untrusted prover maintains records, and trusted verifier certifies a record or entire record set by simply 
      applying sequence of hash operations and signing the commitment (root of the tree)
    * where an untrusted prover requires to prove uniqueness and or freshness of a record
    * where uniqueness of association of entities is required to be proven to Trusted Verifier, to obtain some attestation of 
      association 
    * where different elements of object can be indexed to prove different uniqueness constraint enforcements, that is a leaf may contain more than one index depending on the number of unique factors that an untrusted prover may be required to prove. For example: uniqueness of an idetifier of a record, and uniqueness of association of a record to a value. 
    * where proof of non-existence is required. For example, a unique identifier in a database / record set needs to be unique. But, if Trusted Verifier does not store any records and merely computes hash operations, verifies against state of all records- commitment (root of tree), it is hard to verify uniqueness. By index ordering the tree above assurances/requirements can be met

## Requirements

python 3\
pip install testing.postgresql
pip install sqlalchemy
pip install pg8000

## High level details
The implementation is broken to persistence layer and interface layer. The persistence layer is performed by ```dbiomt.py```. 

**dbiomt.py:** provides persistence functions to store the iomt nodes/leaves in a database table as below with other helper functions

**TVerifier.py:** provides simple verifier functions to verify the commitment (root) for existing root, and updates the root stored in trusted boundary only if the proof vector of complementary nodes is consistentent with existing root. That is, by simply applying sequence of hashes in right order on given proof vector, a leaf can be verified for its membership in an IOMT.

Note: Trusted Verifier functions do not maintain any leaves/intermediate nodes/any parts of tree. The TV is bootstrapped with

IOMT Table:

| indx  | next | value | level | position
--- | --- | ---| --- | ---

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
* `compute_leaf_hash` :    hash of index,value, next - `sha2(index,value,next)`
* `compute_parent_hash`: This parent hash is slightly different, where if the `value` is `None` then the other value is returned. For example if left node value is `None` the right node value is returned as parent node hash. `why?: ` for large trees we don't have to store the intermediate nodes, and not have to compute intermediate hashes, as `f(h1,h2):=h1, if h2==0`, and `f(h1,h2):=h2, if h1==0`

* `buildIOMT`: Builds IOMT for given leaves of IOMT
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

## Sample output
![Alt text](Sample_Output_IOMT.png?raw=true "Sample IOMT output")



