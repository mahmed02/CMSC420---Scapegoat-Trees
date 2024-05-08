from __future__ import annotations
import json
import math
from typing import List

# Node Class
# You may make minor modifications.

class Node():
    def  __init__(self,
                  key        = None,
                  value      = None,
                  leftchild  = None,
                  rightchild = None,
                  parent     = None):
        self.key        = key
        self.value      = value
        self.leftchild  = leftchild
        self.rightchild = rightchild
        self.parent     = parent

# Scapegoat Tree Class.
# DO NOT MODIFY.
class SGtree():
    def  __init__(self,
                  a    : int  = None,
                  b    : int  = None,
                  m    : int  = None,
                  n    : int  = None,
                  root : Node = None):
        self.m     = 0
        self.n     = 0
        self.a     = a
        self.b     = b
        self.root  = None

    # For the tree rooted at root, dump the tree to stringified JSON object and return.
    def dump(self) -> str:
        def _to_dict(node) -> dict:
            pk = None
            if node.parent is not None:
                pk = node.parent.key
            return {
                "k": node.key,
                "v": node.value,
                "l": (_to_dict(node.leftchild)  if node.leftchild  is not None else None),
                "r": (_to_dict(node.rightchild) if node.rightchild is not None else None)
            }
        if self.root == None:
            dict_repr = {}
        else:
            dict_repr = _to_dict(self.root)
        return json.dumps(dict_repr,indent=2)

    def insert(self, key: int, value: str):
        self.n = self.n + 1

        if self.n > self.m:
            self.m = self.n

        if self.root == None:
            self.root = Node(key=key,value=value)
        else:
            node, depth = self.ol_insert(self.root,key,value,1)

            # scapegoat exists, rebuild
            if depth > self.my_log(self.n):
                scapegoat = self.find_scapegoat(node, None)
                list = self.gather(scapegoat)
                new_node = self.rebuild(list, scapegoat.parent)
                # if the scapegoat is the root
                if scapegoat.parent == None:
                    self.root = new_node
                else:
                    par = scapegoat.parent

                    # first check if left child exists, then check if its the scapegoat
                    if par.leftchild != None:
                        if par.leftchild.key == scapegoat.key:
                            par.leftchild = new_node
                        else:
                            par.rightchild = new_node
                    else:
                        par.rightchild = new_node

                    scapegoat.parent = None # destroy scapegoat
                         

    def ol_insert(self, cur: Node, key: int, value: str, depth: int) -> tuple[Node, int]:
        if key > cur.key:
            if cur.rightchild == None:
                to_insert = Node(key = key, value = value, parent = cur)
                cur.rightchild = to_insert
                return to_insert,depth
            else:
                return self.ol_insert(cur.rightchild,key,value,depth+1)
        else:
            if cur.leftchild == None:
                to_insert = Node(key = key, value = value, parent = cur)
                cur.leftchild = to_insert
                return to_insert,depth
            else:
                return self.ol_insert(cur.leftchild,key,value,depth+1)
            
    def my_log(self, x: int) -> float:
        return math.log(x) / math.log(self.b / self.a)
    
    def find_scapegoat(self, cur: Node, child: Node) -> Node:
        if self.size(child)/self.size(cur) > self.a/self.b:
            return cur
        return self.find_scapegoat(cur.parent,cur)

    def size(self, cur: Node) -> int:
        if cur == None:
            return 0
        return 1 + self.size(cur.leftchild) + self.size(cur.rightchild)
    
    def gather(self, cur: Node) -> List[tuple[int, str]]:
        if cur == None:
            return []
        return self.gather(cur.leftchild) + [(cur.key,cur.value)] + self.gather(cur.rightchild)
    
    def rebuild(self,content:list[tuple[int,str]], par: Node) -> Node:
        if len(content) == 0:
            return None
        
        length = len(content)
        mid = length//2
        new_key, new_value = content[mid]
        new_root = Node(key=new_key, value=new_value, parent = par)
        left = content[:mid]
        right = content[mid+1:]
        new_root.leftchild = self.rebuild(left, new_root)
        new_root.rightchild = self.rebuild(right, new_root)

        return new_root
    
    def destroy(self, cur: Node):
        if cur == None:
            return
        self.destroy(cur.leftchild)
        self.destroy(cur.rightchild)
        cur.leftchild = None
        cur.rightchild = None
        cur.parent = None

    def delete(self, key: int):
        self.n = self.n - 1

        if self.n == 0:
            self.root = None
        else:
            self.rec_delete(self.root, key)
        
        if self.n < (self.a/self.b) * self.m:
            self.m = self.n
            self.root = self.rebuild(self.gather(self.root),None)


    def rec_delete(self, cur: Node, key:int) -> Node:
        if key > cur.key:
            cur.rightchild = self.rec_delete(cur.rightchild,key)
        elif key < cur.key:
            cur.leftchild = self.rec_delete(cur.leftchild,key)
        else:
            if cur.leftchild == None:
                # set subtree to promote's parent as target nodes' parent
                if cur.rightchild != None:
                    if cur.parent == None:
                        self.root = cur.rightchild
                        self.root.parent = None
                    else:
                        cur.rightchild.parent = cur.parent

                # remove connection to other nodes for garbage collector
                to_return = cur.rightchild
                cur.rightchild = None
                cur.parent = None

                return to_return
            elif cur.rightchild == None:
                # set subtree to promote's parent as target nodes' parent
                if cur.leftchild != None:
                    if cur.parent == None:
                        self.root = cur.leftchild
                        self.root.parent = None
                    else:
                        cur.leftchild.parent = cur.parent

                # remove connection to other nodes for garbage collector
                to_return = cur.leftchild
                cur.leftchild = None
                cur.parent = None

                return to_return
            else:
                ios = self.min(cur.rightchild)
                cur.key = ios.key
                cur.value = ios.value
                cur.rightchild = self.rec_delete(cur.rightchild, ios.key)
        return cur
    
                # set parent's pointer to target child to the subtree being promoted
                # (dont know which child of the parent we are) ... dont need this?
                # cur.parent.leftchild.key == key:
                #    cur.parent.leftchild = cur.rightchild
                #else:
                #    cur.parent.rightchild = cur.rightchild
    
    def min(self,cur: Node) -> Node:
        if cur.leftchild != None:
            return self.min(cur.leftchild)
        return cur

    def search(self, search_key: int) -> str:
        return json.dumps(self.rec_search(self.root,search_key))

    def rec_search(self, cur: Node, key: int) -> str:
        if key > cur.key:
            return [cur.value] + self.rec_search(cur.rightchild, key)
        elif key < cur.key:
            return [cur.value] + self.rec_search(cur.leftchild, key)
        return [cur.value]