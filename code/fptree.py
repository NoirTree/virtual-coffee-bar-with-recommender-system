# -*- coding: utf-8 -*-
"""
Created on Wed May 5 19:15:00 2020

@author: Jingxuan Huang
"""

class Node:
    """
    Node
    公有成员：
    * item：str, 项目名
    * parent：Node, 祖先节点
    * support_count：int, 支持度计数
    * next_sibling：Node, fptree中该item的下一个同名节点位置
    * childrens_dict: dict{key = item, value = Node}, 该节点的子女列表，用哈希表存储，键为项目名，值为对应的节点
    """
    def __init__(self, item, parent, support_count = 1):
        """
        初始化一个节点。
        * param item: str, 项目名
        * param parent: Node, 祖先节点
        * param support_count: int, 支持度计数(默认为1)
        """
        self.item = item
        self.parent = parent
        self.support_count = support_count
        self.next_sibling = None
        self.childrens_dict = dict()
    
    def get_child(self, child_item):
        """
        返回名为child_item的子女节点
        * param child_item: str, 子女节点名
        * return: Node, 该子女节点/None, 不存在指定子女节点
        """
        return self.childrens_dict.get(child_item, None)
        
    
    def add_child(self, new_child_item):
        """
        为该节点添加一个名为new_child_item的子女节点。
        若已有同名子女，则直接返回子女节点。
        * param new_child_item: str, 子女节点名
        * return: Node, 该子女节点
        """
        if new_child_item in self.childrens_dict:
            return self.childrens.dict[new_child_item]
        else:
            new_child = Node(new_child_item, self)
            self.childrens_dict[new_child_item] = new_child
            return new_child

class FPtree:
    """
    FPtree对象
    * 私有成员:
        __header_table:项头表
        (用self.自动挑出来的那些康康到低有哪些。。。)
        
    * 内部方法：
        * __init_header_table(self): 初始化项头表
    * 外部接口：
        * fpgrow(min_support): 挖掘高于支持度阈值的频繁模式
    """
    def __init__(self, transactions):
        '''初始化'''
        self.transactions = transactions #读入历史消费记录(list(list))        
    
    def fpgrow(self, min_support = 2, min_len = 2, max_len = 9): 
        """
        挖掘支持度高于min_support的频繁模式。
        * param min_support: int, 支持度计数阈值
        * return: dict, 挖掘结果，{频繁模式:支持度}
        """
        while(min_len > max_len):
            print("The minimal length cannot larger than the maximal length! Please input again.")
            min_len = eval(input("minimal length:"))
            max_len = eval(input("maximal length:"))
        if min_support:
            self.min_support = min_support
        self.min_len = min_len
        self.max_len = max_len
        try:
            self.__init_header_table() #生成项头表
            self.__construct_fptree() #构建FPTree
            self.__mine_frequent_pattern() #挖掘频繁项集
        except Exception as err:
            return err
        else:
            return True
        
    
    
    def __init_header_table(self):
        """
        生成项头表。
        """
        from collections import OrderedDict
        
        #扫描交易记录，统计每个项目的频度
        self.item_frequency = dict()
        for trans in self.transactions: #对于每条购买记录
            for item in trans: #对于每条购买记录中的每件商品
                self.item_frequency[item] = self.item_frequency.get(item, 0)+1
        self.max_frequency = max(self.item_frequency.values())
        
        #筛掉低于阈值的项目, 余下项目按频次降序排列
        items_freq = list(filter(lambda x: x[1]>=self.min_support, self.item_frequency.items()))
        self.items_seq = [x[0] for x in sorted(items_freq, key = lambda x:x[1], reverse = True)]
        #初始化项头表，将节点域设置为None
        self.__header_table = OrderedDict()
        for item in self.items_seq:
            self.__header_table[item] = None
        
        #将购买记录中低于阈值的项目筛掉，再按项头表次序排列后，保存在self.__transationcs中
        self.__filter_trans = []
        for trans in self.transactions: #扫描原始交易数据
            remain_items = list(set(trans) & set(self.items_seq)) #取交集，筛选
            trans = list(sorted(remain_items, key = self.items_seq.index))
            if trans != []:
                self.__filter_trans.append(trans)
        #print(self.__filter_trans)
        
    
    def __construct_fptree(self):
        """
        构建FPTree。
        """
        self.__root = Node('null', None, 0) #根节点置空
        #重新读取__filter_trans中的交易记录
        for trans in self.__filter_trans:
            self.__insert_trans(self.__root, trans) #递归地插入每一条交易记录
        
    def __insert_trans(self, root, trans):
        """
        向根节点递归地插入交易记录。
        * param root: Node, 根节点
        * param trans: list, 一条交易记录
        """
        if trans == []: #读取完毕(base case)
            return
        else:
            child = root.get_child(trans[0]) #查找第一项是否在根节点的孩子列表中
            if child is None: #如果不存在
                child = root.add_child(trans[0]) #则生成一个新节点
                #修改该节点对应的项头表与next_sibling指针
                next_node = self.__header_table.get(trans[0], None)
                if next_node is None: #如果项头表中该项目还没有记录
                    self.__header_table[trans[0]] = child #则直接指向该节点
                else: #否则，找到链表的最后一项，再指向该节点
                    while next_node.next_sibling is not None:
                        next_node = next_node.next_sibling
                    next_node.next_sibling = child
            else: #如果已存在
                child.support_count += 1 #则该孩子的支持度计数+1
                
            self.__insert_trans(child, trans[1:]) #以该孩子节点为根，递归插入余下的记录


    def __mine_frequent_pattern(self):
        """
        挖掘频繁项集。
        """
        self.__item_cond_pattern_base = dict()
        #寻找每一项的条件模式基
        for item in self.__header_table:
            next_node = self.__header_table[item]
            __parent_support_count = dict()
            while next_node is not None: #遍历每一个以该商品为根节点
                parent = next_node.parent #parent是Node类型
                while parent.item != 'null': # 当祖先不是null根节点时
                    #加上该分支最小支持度计数（next_node叶节点的支持度计数是该分支上最小的）
                    __parent_support_count[parent.item] = __parent_support_count.get(parent.item, 0)+next_node.support_count
                    parent = parent.parent #向上溯源
                next_node = next_node.next_sibling #往下一个分支寻找
            self.__item_cond_pattern_base[item] = __parent_support_count

        #筛掉支持度不满足阈值的条件模式基节点
        for item, cond_pattern_base in self.__item_cond_pattern_base.items():
            filter_cond_pattern_base = dict()
            for parent_item, parent_count in cond_pattern_base.items():
                if parent_count >= self.min_support:
                    filter_cond_pattern_base[parent_item] = parent_count
            self.__item_cond_pattern_base[item] = filter_cond_pattern_base

        #递归挖掘频繁项集
        self.freq_pattern_frequency = dict() #结果集合
        from itertools import combinations #排列组合函数
        for item, parent_frequency_dict in self.__item_cond_pattern_base.items():
            #频繁一项集; 如果限制频繁项集长度，可能需要修改
            #if self.min_len <= 1:
            #    self.freq_pattern_frequency[(item,)] = self.item_frequency[item]
            #频繁2~n项集：排列组合
            if self.max_len > 1:
                for size in range(self.min_len-1, self.max_len):
                    for other_items in combinations(parent_frequency_dict.keys(), size):
                        #一条项目中支持度最小的为该条规则的支持度
                        #if other_items:
                        #   print([parent_frequency_dict[x] for x in other_items])
                        if other_items:
                            self.freq_pattern_frequency[other_items+(item,)] = min([parent_frequency_dict[x] for x in other_items])

    def getrules(self):
        '''返回频繁模式(dict){频繁模式:支持度}，没有则返回false'''
        if len(self.freq_pattern_frequency) == 0:
            return False
        else:
            return self.freq_pattern_frequency
                
    def gettoprules(self, top = 5):
        '''打印支持度最高的top条模式，默认top5；若支持度相同，则长的规则优先'''
        sort_pattern_frequency = [x for x in sorted(self.freq_pattern_frequency.items(), key = lambda x: (x[1], len(x[0])), reverse = True)]
        top_items = sort_pattern_frequency[:top-1]
        top_pattern_frequency = {}
        for item in top_items:
            top_pattern_frequency[item[0]] = item[1]
        return top_pattern_frequency
    
    def saverules(self):
        '''将规则保存到数据库，成功返回True，失败返回错误名'''
        try:
            res_list = []
            for pattern, frequency in self.freq_pattern_frequency.items():
                pattern = set(pattern)#将规则转成集合类型储存（便于查找运算）
                res = ','.join(pattern)+':'+str(frequency)+'\n'
                res_list.append(res)
    
            with open('patterns.txt', 'w', encoding = 'utf-8') as f:
                f.writelines(res_list)
        except Exception as err:
            return err
        else:
            return True