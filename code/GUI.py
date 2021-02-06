# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 18:21:25 2020

@author: lenovo
"""

import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
from starbuck import *
import random
user = User()
root = tk.Tk()
root.title('My coffee bar')
#root.geometry('650x300')
root.resizable(0, 0)
screenWidth = root.winfo_screenwidth()  # 获取显示区域的宽度
screenHeight = root.winfo_screenheight()  # 获取显示区域的高度
left = (screenWidth - 650) / 2
top = (screenHeight - 300) / 2
root.geometry("650x300+%d+%d" % (left, top))#“长x宽+左+高”

statusText = tk.StringVar()
statusText.set('Welcome! Enjoy your time here~')
busketstatusText = tk.StringVar()

def check_busket():
    '''跳出busket弹窗'''
    busketwin = tk.Toplevel(root)
    busketwin.title('My Busket')
    busketmainframe = tk.Frame(busketwin)
    busketmainframe.pack(side = 'top', fill = 'both', expand = 1)
    busketmenuframe = tk.Frame(busketmainframe)
    busketmenuframe.pack(side = 'left', fill = 'both', expand = 1)
    busketbuttomframe = tk.Frame(busketmainframe)
    busketbuttomframe.pack(side = 'right', fill = 'both', expand = 1)
    #右侧用户购物清单: 名字，个数，价格+总金额
    busketTree = ttk.Treeview(busketmenuframe, columns = ('number', 'price'))
    busketTree.heading('number', text='number')
    busketTree.heading('price', text='price')
    for item, num in user.busket.items():
        busketTree.insert('', 0, item, text = item)
        busketTree.set(item, 'number', str(num))
        busketTree.set(item, 'price', '$'+str(num*user.menu.get_item_price(item)))
    #创建滚动条
    busketmenuScrollBar = ttk.Scrollbar(busketmenuframe, orient = tk.VERTICAL,
                                       command = busketTree.yview)
    busketTree['yscrollcommand'] = busketmenuScrollBar
    busketmenuScrollBar.pack(side = 'right', fill = 'y')
    busketTree.pack(side = 'top', fill = 'both', expand = 1, anchor = 'ne')

    tk.Label(busketmenuframe, text = 'Tips: You can delete an item by change it number to 0!',
             font="Helvetica 9").pack(side = 'bottom', fill = 'x', expand = 1, anchor = 'e')

    def change_the_number():
        '''修改数量'''
        try:
            item = busketTree.item(busketTree.focus(), 'text')
            num = eval(busketspinval.get())
            user.reset_nums_item(item, num)
            busketstatusText.set('You have changed '+item+' to '+
            str(num)+' Successively!')
            userTotal.set(user.total)
            #更新推荐
            recommend_item = user.recommendation()
            if recommend_item:
                recommendItem.set(', '.join(recommend_item))
            else:
                #随机推荐一个商品
                recommendItem.set(random.choice(list(user.menu.checkall().keys())))
        except:
            busketstatusText.set('Please input correct item number!')
        #修改TreeView
        if num == 0 and item != '':
            busketTree.delete(item)
        elif item == '':
            busketstatusText.set('Please select an item first!')
        else:
            busketTree.set(item, 'number', str(num))
            busketTree.set(item, 'price', '$'+str(num*user.menu.get_item_price(item)))

    def clean_busket():
        '''清空购物篮'''
        chos = tk.messagebox.askyesno(title = 'Warning', message = 'Are you really sure to delete all items in the busket?')
        if chos:
            for item in user.busket:
                busketTree.delete(item)
            user.clean_busket();
            userTotal.set(0)
            tk.messagebox.showinfo(title = 'Info', message = 'The busket has been cleaned up successfully!')
            busketstatusText.set('The busket has been cleaned up successfully!')

    def pay_in_busket():
        items = user.busket
        if user_pay(): #支付成功时，才清空树形表中元素
            for item in items:
                busketTree.delete(item)


    ##右侧用户界面
    #数字选择spinbox
    busketspinval = tk.StringVar()
    busketspinval.set(1)
    busketspinbox = ttk.Spinbox(busketbuttomframe, from_ = 0, to = 999,
                          textvariable = busketspinval, width = 16)
    busketspinbox.pack(side = 'top', fill = 'x', anchor = 'n')
    #修改商品数量按钮
    changeBusketButton = tk.Button(busketbuttomframe,
                                  text = 'change the number',
                                  width = 16,
                                  command = change_the_number)
    changeBusketButton.pack(side = 'top', fill = 'x', anchor = 'n')

    #一键清空
    cleanBusketButton = tk.Button(busketbuttomframe,
                                  text = 'clean up',
                                  width = 16,
                                  command = clean_busket)
    cleanBusketButton.pack(side = 'top', fill = 'x', anchor = 'n')

    #结算按钮
    busketPayButton = tk.Button(busketbuttomframe,
                          text = 'pay now',
                          width = 16,
                          command = pay_in_busket)
    busketPayButton.pack(side = 'top', fill = 'x', anchor = 'n')

    #显示总金额等信息
    busketuserInfoFrame = tk.Frame(busketbuttomframe)
    busketuserInfoFrame.pack(side = 'top', fill = 'both', expand = 1)
    tk.Label(busketuserInfoFrame, text = 'Your payment is:').pack(side = 'top', fill = 'x', anchor = 'ne')
    buskettotalLabel = tk.Label(busketuserInfoFrame, textvariable = userTotal)
    buskettotalLabel.pack(side = 'top', fill = 'x', anchor = 'ne')


    #状态栏
    busketstatusBar = tk.Label(busketwin, textvariable = busketstatusText,
                         relief = tk.SUNKEN)
    busketstatusBar.pack(side = 'bottom', fill = 'x', expand = 1, anchor = 'w')

#-------------------------------------------------------------------------
#主页面
#-------------------------------------------------------------------------
def add_to_busket():
    '''加入购物车'''
    try:
        item = menutree.item(menutree.focus(), 'text')
        num = int(spinval.get())
        if user.add_item(item, num):
            statusText.set('You have added '+str(num)+' '+item+
            ' successively!')
            userTotal.set(user.total)
            #更新推荐
            recommend_item = user.recommendation()
            if recommend_item:
                recommendItem.set(','.join(recommend_item))
            else:
                #随机推荐一个商品
                recommendItem.set(random.choice(list(user.menu.checkall().keys())))
    except:
        statusText.set('Please input correct item number!')

def add_recomd_to_busket():
    '''将推荐商品加入购物车'''
    items = recommendItem.get().split(',')
    if items == ['']:
        return
    num = 1
    status = True
    for item in items:
        status = user.add_item(item, num)
    if status:
        statusText.set('You have added the recommended item '+ ', '.join(items)
                       +' successively!')
        userTotal.set(user.total)
        #更新推荐
        recommend_item = user.recommendation()
        if recommend_item:
            recommendItem.set(','.join(recommend_item))
        else:
            #随机推荐一个商品
            recommendItem.set(random.choice(list(user.menu.checkall().keys())))
    else:
        tk.messagebox.showinfo(title = 'Error', message = 'Oops. Something goes wrong! Please try again.')

def user_pay():
    '''用户支付'''
    mes = 'Your total payment is '+str(user.total)+'. Are you sure to pay now?'
    var = tk.messagebox.askyesno(title = 'Payment Confirm', message = mes)
    if var:
        try:
            res = user.pay()
        except Empty:
            tk.messagebox.showerror(title = 'Payment Fail', message = "You haven't chosen anything yet!")
            return False
        else:
            if res:
                #支付后，total和购物车清空
                user.total = 0
                userTotal.set(user.total)
                user.clean_busket()
                tk.messagebox.showinfo(title = 'Payment Successful', message = 'Payment Successful!')
                return True
            else:
                tk.messagebox.showerror(title = 'Payment Fail', message = 'Payment failed! Please try again.')
                return False



#基本框架
mainframe = tk.Frame(root)
mainframe.pack(side = 'top', fill = 'both', expand = 1)
menuframe = tk.Frame(mainframe)
menuframe.pack(side = 'left', fill = 'both', expand = 1)
buttomframe = tk.Frame(mainframe)
buttomframe.pack(side = 'right', fill = 'both', expand = 1)

##左侧菜单
#创建菜单
menutree = ttk.Treeview(menuframe, columns = ('price'))
menutree.heading("#0",text="Name")#树标题设置名字
menutree.heading('price', text='price')
for item in user.menu.item_price:
    menutree.insert('', 0, item, text = item)
    menutree.set(item, 'price', '$'+str(user.menu.get_item_price(item)))
#创建滚动条
menuScrollBar = ttk.Scrollbar(menuframe, orient = tk.VERTICAL,
                                   command = menutree.yview)
menutree['yscrollcommand'] = menuScrollBar
menuScrollBar.pack(side = 'right', fill = 'y')
menutree.pack(side = 'top', fill = 'both', expand = 1, anchor = 'ne')

#推荐页面
recommendTitle = tk.Label(menuframe, text = 'You may also like:', relief = tk.RIDGE,
                          width = 10, bg = 'tan')
recommendTitle.pack(side = 'left', fill = 'x', expand = 1, anchor = 'ne')
recommendItem = tk.StringVar()
recommendLabel = tk.Label(menuframe, textvariable = recommendItem, relief = tk.RIDGE,
                          width = 10, bg = 'pink')
recommendLabel.pack(side = 'right', fill = 'both', expand = 1, anchor = 'ne')

##右侧用户界面
#数字选择spinbox
spinval = tk.StringVar()
spinval.set(1)
spinbox = ttk.Spinbox(buttomframe, from_ = 1, to = 999,
                      textvariable = spinval, width = 20)
spinbox.pack(side = 'top', fill = 'x', anchor = 'n')
#加入购物车按钮
addToBusketButton = tk.Button(buttomframe,
                              text = 'add to busket',
                              width = 20,
                              command = add_to_busket)
addToBusketButton.pack(side = 'top', fill = 'x', anchor = 'n')
#查看购物车按钮
checkBusketButton = tk.Button(buttomframe,
                              text = 'check my busket',
                              width = 20,
                              command = check_busket)
checkBusketButton.pack(side = 'top', fill = 'x', anchor = 'n')
#结算按钮
payButton = tk.Button(buttomframe,
                      text = 'pay now',
                      width = 20,
                      command = user_pay)
payButton.pack(side = 'top', fill = 'x', anchor = 'n')
#显示总金额等信息
userInfoFrame = tk.Frame(buttomframe)
userInfoFrame.pack(side = 'top', fill = 'both', expand = 1)
userTotal = tk.StringVar()
userTotal.set(0)
tk.Label(userInfoFrame, text = 'Your payment is:').pack(side = 'top', fill = 'x', anchor = 'ne')
totalLabel = tk.Label(userInfoFrame, textvariable = userTotal)
totalLabel.pack(side = 'top', fill = 'x', anchor = 'ne')

addRecomdButton = tk.Button(buttomframe,
                            text = '←add it to the busket',
                            width = 20,
                            bg = 'yellow',
                            command = add_recomd_to_busket)
addRecomdButton.pack(side = 'bottom', fill = 'x', anchor = 'n')

#状态栏
statusBar = tk.Label(root, textvariable = statusText,
                     relief = tk.SUNKEN, height = 1)
statusBar.pack(side = 'bottom', fill = 'x', expand = 1, anchor = 'w')

root.mainloop()