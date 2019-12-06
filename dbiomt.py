import sqlite3
from sqlite3 import Error

class IOMT_DB:
    def __init__(self,db_file):
        self.db_file  =   db_file
        self.init_iomt_db()
     
    
    def init_iomt_db(self):
        sql_create_iomt_table = """ CREATE TABLE IF NOT EXISTS iomt (
                                        indx integer,
                                        next integer,
                                        value text,
                                        level integer NOT NULL,
                                        position integer NOT NULL
                                    ); """
        conn = self.create_connection()
        if conn is not None:
            self.create_table(conn, sql_create_iomt_table)

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except Error as e:
            print(e)
        return conn

    def create_table(self,conn, create_table_sql):
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)
   
    def create_iomt_record(self,conn, iomt_record):
        place_holder=self.get_min_place_holder_position(conn,iomt_record[3])
        #print('place_holder',place_holder)
        if place_holder is None or iomt_record[0] is None or iomt_record[3]>0:
            sql = ''' insert into iomt(indx,next,value,level,position)
                    values(?,?,?,?,?) '''
            cur = conn.cursor()
            cur.execute(sql, iomt_record)
            return cur.lastrowid
        else:
            cur=conn.cursor()
            print(iomt_record[0],iomt_record[1],iomt_record[2],place_holder)
            cur.execute("Update iomt set indx=?,next=?,value=? where level=0 and position=?",[iomt_record[0],iomt_record[1],iomt_record[2],place_holder])
            return cur.lastrowid

            
    
    def check_enclosure(self,conn,new_indx):
        cur = conn.cursor()
        cur.execute("select indx,next from iomt where level=0 and indx<? and next>?",[new_indx,new_indx])
        rows = cur.fetchall()
        if len(rows)>0:
            return [rows[0][0],rows[0][1]]
        else:
            return None

    def get_min_iomt(self,conn):
        cur = conn.cursor()
        cur.execute("select min(indx) from iomt where level=0")
        count = cur.fetchall()
        return count[0][0]
    
    def set_next_of_cur_max_iomt(self,conn,new_next):
        max=self.get_max_iomt(conn)
        cur=conn.cursor()
        cur.execute("Update iomt set next=? where level=0 and indx=?",[new_next,max])
        return cur.lastrowid
    '''
         get the interval, 
         modify that leaf so that the next of the leaf is index, and index next is the fit interval's next
    '''
    def split_interval_iomt(self,conn,new_index,old_index,value):
        leaf=self.get_iomt_leaf_with_index(conn,old_index)
        leaf_count=self.get_iomt_leaf_count(conn)
        if leaf is not None:
            iomt_record=(new_index,leaf[1],value,0,leaf_count)
            self.create_iomt_record(conn,iomt_record)
            cur=conn.cursor()
            cur.execute("Update iomt set next=? where level=0 and indx=?",[new_index,old_index])
            return cur.lastrowid

    def set_min_indx_iomt(self,conn,new_min_index,value):
        cur_min=self.get_min_iomt(conn)
        leaf_count=self.get_iomt_leaf_count(conn)
        iomt_record=(new_min_index,cur_min,value,0,leaf_count)
        self.create_iomt_record(conn,iomt_record)
        self.set_next_of_cur_max_iomt(conn,new_min_index)

    '''
        set new max, that is -> next of current max to new max, and new max next to min
    '''
    def set_max_indx_iomt(self,conn,new_max_index,value):
        cur_min=self.get_min_iomt(conn)
        leaf_count=self.get_iomt_leaf_count(conn)
        iomt_record=(new_max_index,cur_min,value,0,leaf_count)
        self.set_next_of_cur_max_iomt(conn,new_max_index)
        self.create_iomt_record(conn,iomt_record)
        

    def get_max_iomt(self,conn):
        cur = conn.cursor()
        cur.execute("select max(indx) from iomt where level=0")
        count = cur.fetchall()
        return count[0][0]

    def get_iomt_leaf_count(self,conn):
        cur = conn.cursor()
        cur.execute("select count(*) from iomt where level=0")
        count = cur.fetchall()
        return count[0][0]

    def get_iomt_leaf_with_index(self,conn, indx):
        cur = conn.cursor()
        cur.execute("select * from iomt where indx=? and level=0", [indx])
        rows = cur.fetchall()
        return rows[0]
    
    def get_iomt_leaf_at_pos(self,conn, position):
        cur = conn.cursor()
        cur.execute("select * from iomt where position=? and level=0", [position])
        rows = cur.fetchall()
        return rows[0]
    
    def get_min_place_holder_position(self,conn,level):
        cur = conn.cursor()
        #print('placeholder_level',level)
        cur.execute("select min(position) from iomt where indx is NULL and level=?",[level])
        rows = cur.fetchall()
        if len(rows)>0 and level==0:
            return rows[0][0]
        else:
            return None

    def get_root(self,conn):
        cur = conn.cursor()
        cur.execute("select * from iomt where level=(select max(level) from iomt)")
        rows = cur.fetchall()
        if len(rows)>0:
            return rows[0][2]
        else:
            return None

    def get_node_at(self,conn,level,position):
        cur = conn.cursor()
        #print('getnode_at',level,position)
        cur.execute("select * from iomt where level=? and position=?", [level,position])
        rows = cur.fetchall()
        return rows[0]

    def get_iomt_node_count_at_level(self,conn,level):
        cur = conn.cursor()
        cur.execute("select count(*) from iomt where level=?",[level])
        rows = cur.fetchall()
        if len(rows)>0:
            return rows[0][0]
        else:
            return None
    
    def print_iomt_leaves(self,conn):
        cur = conn.cursor()
        cur.execute("select * from iomt where level=0")
        rows = cur.fetchall()
        for row in rows:
            print(row)
    
    def print_iomt_nodes(self,conn):
        cur = conn.cursor()
        cur.execute("select * from iomt where level>0 order by level")
        rows = cur.fetchall()
        for row in rows:
            print(row)

    def max_level(self,conn):
        cur = conn.cursor()
        cur.execute("select max(level) from iomt where")
        rows = cur.fetchall()
        return rows[0][0]

