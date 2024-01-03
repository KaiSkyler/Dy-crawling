import os  # 创建文件夹, 文件是否存在
import time  # time 计时
import pickle  # 保存和读取cookie实现免登陆的一个工具
import json
import threading
from time import sleep
from selenium import webdriver  # 操作浏览器的工具
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pynput.keyboard import Listener, Key, Controller

class DouYin:
    # 初始化加载
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.targetUrl = "https://www.douyin.com/" #抖音推荐视频抓取地址
        self.isActiveVideoClass = "xgplayer-playing xgplayer-inactive" #正在播放视频的class
        self.videoInfoId = "video-info-wrap" #视频信息id样式
        self.isLoginElementId = "Cn2CzO_Q" #未登录的元素id标识
        self.commentListClass = "comment-mainContent" #评论区列表class
        self.commentContentClass = "j5WZzJdp" #评论区的内容class
        self.commentItemClass = "xzjbH9pV" #评论区每个item的class
        self.accountNameClass = "account-name" #视频账号名称
        self.userAvatarClass = "avatar-component-avatar-container" #用户头像class
        self.accountNameSpanClass = "j5WZzJdp" #用户名中的spanClass
        self.pausePropValue = "PAUSE_TIPS" #锁定视频播放标签属性
        self.userNameClass = "ChwkdccW" #用户昵称class
        self.userName = "missli" #用户昵称
        self.loginState = False #是否登录标识
        self.startTask = False #是否开始任务
        self.isOpenComment = False #是否打开了评论区
        self.currentSaveContentArray = [] #当前保存的内容数组
        self.currentVideoInfo = "" #当前视频信息
        self.saveVideoInfoName = "" #要保存的视频信息名称
        self.isSaveComment = False #是否保存视频
        self.crawling = False #是否抓取视频中

    # 启动命令
    def startUp(self):
        # 启动线程执行
        thread = threading.Thread(target=self.run_chrome_start)
        thread.start()
        # 创建监听器
        listener = Listener(on_press=self.listenSaveOptionsPress)
        # 启动监听器
        listener.start()
        # 进入监听状态
        listener.join()
    
    #创建一个新线程来执行其他代码
    def run_chrome_start(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        chrome_options.add_argument("--disable-popup-blocking") # 禁用弹出窗口阻止

        # 创建Chrome浏览器实例时，直接将选项传递给options参数
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(self.targetUrl)
        if self.driver.execute_script("return document.readyState") == "complete":
            while True:
                try:
                    if not self.loginState:
                        self.checkLogin()
                    if self.loginState and not self.crawling:
                        self.doTask()
                except Exception as e:
                    pass

    # 检查是否登录
    def checkLogin(self):
        #logDiv = self.driver.find_element(By.ID, self.isLoginElementId)
        #logText = logDiv.find_element(By.XPATH, "./*")
        #print(logText.get_attribute('innerHTML'))
        userNameElement = self.driver.find_element(By.CLASS_NAME, self.userNameClass)
        userName = userNameElement.get_attribute('innerHTML')
        if self.userName == userName:
            self.loginState = True

    # 执行操作
    def doTask(self):
        if self.startTask:
            # 标记抓取中
            self.crawling = True
            print('开始获取视频信息，进行解析...')
            # 模拟键盘按键X键，打开评论区
            if not self.isOpenComment:
                keyboard = Controller()
                keyboard.press('x')
                keyboard.release('x')
                self.isOpenComment = True
            
            # 获取当前视频信息
            self.getVideoInfo()
            # 获取评论区列表
            self.getCommentList()
    
    # 监听是否保存事件按下
    def listenSaveOptionsPress(self,key):
        print('键盘按下'+str(key))
        try:
            if key.char.lower() == 'q':
                print('开始保存视频信息')
                self.isSaveComment = True
                self.startTask = True
        except Exception as e:
            print('在处理键盘按下事件时发生异常:', str(e))

    # 获取当前视频信息
    def getVideoInfo(self):
        print('获取当前视频信息')
        try:
            # videoInfo = self.driver.find_element(By.CSS_SELECTOR, "[lang-key='isActiveVideoClass']")
            # videoInfo = videoInfo.find_element(By.CSS_SELECTOR, "[lang-key='videoInfoId']")
            # accountName = videoInfo.find_element(By.CSS_SELECTOR, "[lang-key='accountNameClass']")
            # deepestSpan = accountName.find_element(By.CSS_SELECTOR, "[lang-key='accountNameSpanClass']")
            
            # 通过控制器锁定当前播放的视频
            currentVideoController = self.driver.find_element(By.CSS_SELECTOR,"[lang-key='"+str(self.pausePropValue)+"']")

            # 通过控制器找到对应播放视频的标签位置
            for _ in range(4):
                # 寻找上级父标签元素
                currentVideoController = currentVideoController.find_element(By.XPATH, "..")
            videoInfoWrap = currentVideoController

            # 通过视频标签位置找到对应用户信息所在的标签位置
            for _ in range(5):
                # 寻找相邻位置下一个标签元素
                videoInfoWrap = videoInfoWrap.find_element(By.XPATH,'following-sibling::*[1]')
            accountName = videoInfoWrap.find_element(By.XPATH,'.//*[contains(@class, '+str(self.accountNameSpanClass)+')]')
            
            # 通过用户信息标签位置找到当前视频的用户昵称所在标签位置
            for _ in range(7):
                accountName = accountName.find_element(By.TAG_NAME, "span")

            # videoInfo = self.driver.find_element(By.CLASS_NAME, self.isActiveVideoClass)
            # videoInfo = videoInfo.find_element(By.ID, self.videoInfoId)
            # accountName = videoInfo.find_element(By.CLASS_NAME,self.accountNameClass)
            # deepestSpan = accountName.find_element(By.CLASS_NAME, self.accountNameSpanClass)
            # for _ in range(4):
            #     deepestSpan = deepestSpan.find_element(By.TAG_NAME, "span")

            # 获取寻找出来后的用户昵称标签里的具体用户昵称文本
            accountNameText = accountName.get_attribute('innerHTML')

            # 判断是否获取成功
            if accountNameText:
                self.saveVideoInfoName = accountNameText
            
            # 输出提示
            print('保存文件名称：'+str(self.saveVideoInfoName))
        except Exception as e:
            print("视频信息获取错误"+str(e))
            pass

     # 获取评论区
    def getCommentList(self):
        print(str(self.saveVideoInfoName)+'的视频评论信息')

        try:
            # 通过控制器锁定当前播放的视频
            currentVideoController = self.driver.find_element(By.CSS_SELECTOR,"[lang-key='"+str(self.pausePropValue)+"']")
            
            # 通过控制器找到对应播放视频的标签位置
            for _ in range(7):
                currentVideoController = currentVideoController.find_element(By.XPATH, "..")
                videoInfoWrap = currentVideoController
            
            # 寻找相邻位置下一个标签元素，找出评论区元素
            videoSideBar = videoInfoWrap.find_element(By.XPATH,'following-sibling::*[1]')

            # 获取评论区列表
            commentListElements = videoSideBar.find_element(By.XPATH,'.//*[contains(@class, '+str(self.commentListClass)+')]')

            # 获取当前已加载成功的每一项评论列表内容
            commentContentElements = commentListElements.find_elements(By.CLASS_NAME, self.commentItemClass)

            # 判断评论是否获取成功
            if isinstance(commentContentElements, list) and len(commentContentElements) > 0:
                for element in commentContentElements:
                    html_content = element.get_attribute('innerHTML')
                    if html_content and html_content not in self.currentSaveContentArray:
                        print("获取第"+str(len(self.currentSaveContentArray)+1)+"个要保存的数组内容")
                        self.currentSaveContentArray.append(html_content)
                        
                
                print("遍历数组完成,当前已获取数组长度" + str(len(commentContentElements)))   
                print("遍历数组完成,当前保存数组长度" + str(len(self.currentSaveContentArray)))    
                if self.isSaveComment:
                    print('导出保存内容到本地'+str(self.saveVideoInfoName)+'.txt')
                    with open(str(self.saveVideoInfoName)+'.txt', 'w', encoding='utf-8') as file:
                        for content in self.currentSaveContentArray:
                            file.write(content + '\n')
                            self.isSaveComment = False
                            self.currentSaveContentArray = []
                            self.crawling = False
                            self.startTask = False
        except Exception as e:
            #print(str(e))
            pass

    # 结束命令
    def finish(self):
        self.driver.quit()

if __name__ == '__main__':
    con = DouYin()
    try:
        con.startUp()
    except Exception as e:
        print(e)
        con.finish()   