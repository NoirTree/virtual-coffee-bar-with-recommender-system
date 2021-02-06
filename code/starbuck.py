# -*- coding: utf-8 -*-
"""
Created on Fri May 22 12:26:04 2020

@author: Jingxuan Huang
"""
class Empty(Exception):
    '''异常类，当用户试图删除不存在的商品时冒出'''
    pass

class Menu(object):
    '''
    Description:
        菜单对象
    Attributes:
        item_price(dict): 商品与价格
    '''
    
    def __init__(self):
        #初始化菜单
        with open('menu.txt') as f:
            lines = f.readlines()
            self.item_price = {}
            for line in lines:
                item, price = line.strip().split(':')
                self.item_price[item] = eval(price)


    def get_item_price(self, item):
        '''查找商品价格，若不存在返回false'''
        try:
            return self.item_price[item]
        except:
            return False
    
    def checkall(self):
        '''查询全部商品'''
        return self.item_price        
        
class User(object):
    '''
    Description:
        用户进入系统时自动生成的对象。
    Attributes:
        recordID(str): 订单编号
        busket(dict): 用户购物篮
            {key = 商品名(str), value = 该商品购买个数(int)}
        records(dict): 读入历史购买记录
            {key = recordID(str), value = transaction:该订单下的商品列表(list)}
        menu(Menu): 菜单
        patterns(list(set)): 频繁模式，每条模式用集合表示，按支持度-长度从高到低排序:
        total(float): 总金额
    '''
    
    def __init__(self):
        '''初始化对象'''
        #读入历史记录
        with open('records.txt', encoding = 'utf-8') as f:#导入购买记录
            lines = f.readlines()
            self.records = {}
            for line in lines:
                #1000037:black tea,milk,cake
                line = line.strip().split(':')
                ID, trans = line[0], line[1]
                transaction = trans.split(',')
                self.records[ID] = transaction
        #随机生成7位ID
        from random import randint
        self.recordID = str(randint(1000000, 9999999))
        while self.recordID in self.records:
            self.recordID = str(randint(1000000, 9999999))
        
        #初始化购物篮，并生成菜单对象
        self.busket = {}
        self.menu = Menu()
        self.total = 0
        
        #读入频繁项集
        with open('patterns.txt') as f:
            lines = f.readlines()
            self.patterns = []
            #先排序
            pattern_support = {}
            for line in lines:
                pattern, support = line.strip().split(':')
                pattern_support[pattern] = support
            sort_pattern_frequency = [x for x in sorted(pattern_support.items(), key = lambda x: (x[1], len(x[0])), reverse = True)]
            for pattern_frequency in sort_pattern_frequency:
                item_set = set()
                item_set.update(pattern_frequency[0].split(','))
                self.patterns.append(item_set) 
    
    def check_busket(self):
        '''查询购物篮中已有的全部商品, 若空则返回None'''
        if len(self.busket) == 0: # 购物篮为空
            return None
        else:
            return self.busket
    
    def clean_busket(self):
        '''清空购物篮'''
        self.busket = {}
        self.total = 0
        return True
    
    def reset_nums_item(self, item, num):
        '''重置购物篮中的item，成功返回True，若非法则报错Empty'''
        if item not in self.busket: # 不在购物篮中
            raise Empty('不存在指定商品！')
        elif num < 0:
            return false
        else:
            self.total -= self.busket[item]*self.menu.get_item_price(item)
            self.busket[item] = num
            self.total +=self.busket[item]*self.menu.get_item_price(item)
            if self.busket[item] == 0: # 已经减少到0
                del self.busket[item] # 从购物篮中直接删除商品
            return True
    
    def delete_the_item(self, item):
        '''将item直接删除(无论个数)，成功返回True，若非法则报错Empty'''
        if item not in self.busket: # 不在购物篮中
            raise Empty('不存在指定商品！')
        else:
            del self.busket[item]
            return True
        
    def check_menu(self):
        '''查看全部可选商品；返回dict'''
        return self.menu.checkall()
        
    def add_item(self, item, num = 0):
        '''向购物篮中添加num个item'''
        if num > 0 and self.menu.get_item_price(item):
            self.busket[item] = self.busket.get(item, 0)+num
            self.total += num * self.menu.get_item_price(item)
            return True
        else:
            return False
    
    def recommendation(self):
        '''
        description:
            根据已选商品猜你喜欢
        return:
            若有匹配，则返回模式中还未被选中的项
            若无匹配，返回None
        '''
        item_selected = set()
        item_selected.update(list(self.busket.keys()))
        #在频繁模式中查找有无匹配项
        for pattern in self.patterns:
            if item_selected.issubset(pattern) and pattern != item_selected:
                return pattern-item_selected
        else:
            return None
    
    def pay(self):
        """
        description:
            结算，有四个步骤：
                1.计算价格
                2.将此条购买记录加入事务数据库records.txt
                3.调用fp-tree更新规则，并将规则与支持度保存在文档中
                4.返回价格
        return:
            正常，返回价格(float)
            异常，返回false
        """
        for item, num in self.busket.items():
            self.total += self.menu.get_item_price(item)*num
        
        #只添加非空记录
        if list(self.busket.keys()) != []:
            with open('records.txt', 'a', encoding = 'utf-8') as f:
                #1000037:black tea,milk,cake
                new_record = str(self.recordID)+':'+','.join(list(self.busket.keys()))+'\n'
                f.write(new_record)
        else:
            raise Empty
        
        import fptree as fpt
        self.transactions = list(self.records.values())
        self.transactions.append(list(self.busket.keys()))
        self.fp_tree = fpt.FPtree(self.transactions)
        if self.fp_tree.fpgrow():
            if self.fp_tree.saverules():
                return self.total
        else:
            return False
        
