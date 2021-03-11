from selenium import webdriver
import time
import requests
import base64
import threading

class Libook:
    def __init__(self):
        self.start_url = "https://lfs.bookln.cn/book/sample1.htm?code=23d54c7370&shelfId=36547&share_=70196444"
        self.driver = webdriver.Chrome(executable_path="/opt/homebrew/bin/chromedriver")
        self.i = 1

    def get_content(self):
        img = self.driver.find_element_by_xpath("//*[contains(@class,'page p"+str(self.i)+"')]//img").get_attribute("src")
        return img

    def get_file_content_chrome(self, uri):
        result = self.driver.execute_async_script("""
            var uri = arguments[0];
            var callback = arguments[1];
            var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
            var xhr = new XMLHttpRequest();
            xhr.responseType = 'arraybuffer';
            xhr.onload = function(){ callback(toBase64(xhr.response)) };
            xhr.onerror = function(){ callback(xhr.status) };
            xhr.open('GET', uri);
            xhr.send();
            """, uri)
        if type(result) == int :
            raise Exception("Request failed with status %s" % result)
        return base64.b64decode(result)

    def save_img(self, img_src, filename):
        try:
            if img_src.startswith('blob:') :
                re = self.get_file_content_chrome(img_src)
            else :
                re = requests.get(img_src).content
            with open("./img/"+str(filename)+".png", "wb") as f:
                f.write(re)
        except BaseException as err:
            print(err)
            # 输出出错的链接到errors.txt,并提示
            f_2 = open("./img/errors.txt", "a", encoding='utf-8')
            f_2.write(str(filename)+"\n")
            f_2.close
            print("ERROR!\n出错页码已保存至errors.txt")

    def run(self):
        # 发送请求
        self.driver.get(self.start_url)
        time.sleep(3)
        self.driver.find_element_by_xpath("//span[@class='iconfont nexPage']").click()
        totalPage = int(self.driver.find_element_by_xpath("//*[@class='bottom']/input[@class='inputPage']").get_attribute("value").split('/')[1])
        threads = []
        while self.i <= totalPage:
            # 获取图片url
            img_src = self.get_content()
            print(img_src)
            # 保存图片
            t = threading.Thread(target=self.save_img,args=(img_src, self.i))
            threads.append(t)
            t.start()
            if (self.i % 2) == 1:
                # 奇数下载完点击下一页url
                self.driver.find_element_by_xpath("//span[@class='iconfont nexPage']").click()
                time.sleep(0.5)
            self.i = self.i + 1

        # 等待所有线程推出
        for t in threads:
            t.join()
        self.driver.quit()
if __name__ == '__main__':
    i = Libook()
    i.run()