import time
from datetime import datetime, timedelta

import json
import re
import requests
from playwright.sync_api import Playwright

import CVBB_LOGIN


class CVBB_CGYY:
    def __init__(self, stu_id, stu_pwd, prior_list, verify_usr, verify_pwd, verify_sid, snap_up_mode=True,
                 stadium="主馆", buddy="", debug_mode=False):

        if not stu_id or not stu_pwd or not prior_list or not verify_usr or not verify_pwd or not verify_sid:
            print("Lack of information.")
            exit(-1)

        self.__stu_id = stu_id
        self.__stu_pwd = stu_pwd
        self.__prior_list = prior_list
        self.__verify_usr = verify_usr
        self.__verify_pwd = verify_pwd
        self.__verify_sid = verify_sid
        self.__snap_up_mode = snap_up_mode
        self.__date = None
        self.__buddy = buddy
        self.__headless = not debug_mode
        self.__stadium_str = stadium
        self.__browser = None

        if stadium == "沙河":
            self.__stadium = "/57"
        elif stadium == "副馆":
            self.__stadium = "/39"
        elif stadium == "主馆":
            self.__stadium = "/38"
        else:
            print("Wrong stadium! Check your spelling...")
            exit(-1)

    def __decode(self, img):  # Powered by xxk!
        img = img.strip()

        # 如果 base64 数据的长度不是 4 的倍数，补充 '='
        missing_padding = len(img) % 4
        if missing_padding != 0:
            img += '=' * (4 - missing_padding)

        data = {
            "user": self.__verify_usr,
            "pass2": self.__verify_pwd,  # 使用MD5加密后的密码
            "softid": self.__verify_sid,
            "codetype": 9501,
            "file_base64": img  # Base64编码后的文件数据
        }

        # 发送POST请求
        url = 'https://upload.chaojiying.net/Upload/Processing.php'
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.post(url, json=data, headers=headers)
            response = json.loads(response.text)
            if response['err_no'] != 0:
                print(response['err_str'])
        except Exception as e:
            print(f"Error verifying base64 image: {e}")
            exit(-1)

        position = dict()
        for pos in response['pic_str'].split('|'):
            position[pos.split(',')[0]] = [pos.split(',')[1], pos.split(',')[2]]

        return position

    def __login(self):
        login = CVBB_LOGIN.CVBB_LOGIN(self.__stu_id, self.__stu_pwd)
        login_data = login.run()
        if login_data == 0:
            i = 0
            while login_data == 0 and i < 5:
                time.sleep(2)
                login_data = login.run()
                i += 1
            if login_data == 0 or login_data == -1:
                print("Login failed...")
                exit(-1)
        elif login_data == -1:
            print("Login failed, check your accound info!")
            exit(-1)
        print(f"Login successful, received {login_data['suc_msg']}!")

    def __run(self):
        context = self.__browser.new_context()
        page = context.new_page()
        page.goto("https://sso.buaa.edu.cn/login?service=https://cgyy.buaa.edu.cn/venue-server/sso/manageLogin")
        page.locator("#loginIframe").content_frame.get_by_role("textbox", name="请输入学工号").click()
        page.locator("#loginIframe").content_frame.get_by_role("textbox", name="请输入学工号").fill(self.__stu_id)
        page.locator("#loginIframe").content_frame.get_by_placeholder("请输入密码").click()
        page.locator("#loginIframe").content_frame.get_by_placeholder("请输入密码").fill(self.__stu_pwd)
        page.locator("#loginIframe").content_frame.get_by_role("button", name="登录").click()
        page.wait_for_timeout(3000)
        page.goto("https://cgyy.buaa.edu.cn/venue/venue-reservation" + self.__stadium)

        succeeded = []

        if self.__snap_up_mode:
            now = datetime.now()
            seven_am = now.replace(hour=7, minute=0, second=2, microsecond=0)
            while now < seven_am:
                now = datetime.now()

        for tu in self.__prior_list:
            reserved = []
            page.reload()
            try:
                page.get_by_role("button", name="关闭").click(timeout=3000)
            except TimeoutError as e:
                print(f"Error encountered: {e}. May be the pop-up no longer exists...")
            page.get_by_text(self.__date).click()
            page.locator("thead").locator("i.ivu-icon.ivu-icon-ios-arrow-forward").click()
            page.locator("thead").locator("i.ivu-icon.ivu-icon-ios-arrow-back").click()
            for t1 in tu:
                tt = page.locator("thead[data-v-43ac885a]").text_content().split()
                while t1 not in tt:
                    try:
                        (page.locator("thead[data-v-43ac885a]").
                         locator("i.ivu-icon.ivu-icon-ios-arrow-forward").click(timeout=1000))
                    except TimeoutError as e:
                        print(f"Error encountered: {e}")
                        break
                    tt = page.locator("thead[data-v-43ac885a]").text_content().split()
                try:
                    id1 = tt.index(t1) + 1
                except ValueError:
                    print(f"Not found {t1}! Please check your format.")
                    continue
                cells = page.locator(f"tbody[data-v-43ac885a] tr td:nth-child({id1})")
                for i in range(1, cells.count() - 1):  # no No.1 court for its obstacle
                    if "free" in cells.nth(i).locator("div").first.get_attribute("class"):
                        cells.nth(i).click()
                        reserved.append(cells.nth(i).locator("..").locator("td:nth-child(1)").text_content()
                                        + " " + t1)
                        break
            if not reserved:
                print(f"no more available courts at {tu}! qwq...")
                continue
            if len(reserved) == 1:
                print(f"only found one court at {reserved[0]}. Half a loaf is better than none, however...")

            buddy = page.locator("div.companion_box.pc div div:nth-child(1)")
            if "addBtn" in buddy.get_attribute("class"):
                print("You have no buddy to play with you! What a shame...")
                exit(-1)
            buddy.click()

            btn = page.locator("div.submit_order_box.pc div.action div:nth-child(2)")
            if "disab" in btn.get_attribute("class"):
                print("I can't press the submit button! Check out the website for reason...")
                exit(-1)  # expected to solve for other things...
            btn.click()

            # solve verify code
            img = page.locator("div.mask div.verifybox div.verifybox-bottom \
                                div div.verify-img-out div.verify-img-panel img")
            img_base64 = img.get_attribute("src").split(',')[1]
            text = page.locator("div.mask div.verifybox div.verifybox-bottom \
                                div div.verify-bar-area").text_content()
            text = re.search(r'【(.*?)】', text).group(1).split(',')
            position = self.__decode(img_base64)
            bbox = img.bounding_box()

            for t in text:
                x_offset = bbox['x'] + int(position[t][0])
                y_offset = bbox['y'] + int(position[t][1])
                page.mouse.click(x_offset, y_offset)
                page.wait_for_timeout(500)

            succeeded = reserved
            break

        context.close()

        return succeeded

    def __buddy_check(self):
        context = self.__browser.new_context()
        page = context.new_page()
        page.goto("https://sso.buaa.edu.cn/login?service=https://cgyy.buaa.edu.cn/venue-server/sso/manageLogin")
        page.locator("#loginIframe").content_frame.get_by_role("textbox", name="请输入学工号").click()
        page.locator("#loginIframe").content_frame.get_by_role("textbox", name="请输入学工号").fill(self.__stu_id)
        page.locator("#loginIframe").content_frame.get_by_placeholder("请输入密码").click()
        page.locator("#loginIframe").content_frame.get_by_placeholder("请输入密码").fill(self.__stu_pwd)
        page.locator("#loginIframe").content_frame.get_by_placeholder("请输入密码").press("Enter")
        page.wait_for_timeout(3000)
        page.goto("https://cgyy.buaa.edu.cn/venue/venues/buddies")

        buddy_data = page.locator("div.responsiveTable div div div table tbody").text_content()

        if "没有加载到数据" in buddy_data:
            if self.__buddy == "":
                print("No buddy to play with you? Contact the author and you will find a good friend... XD")
                exit(-1)
            page.get_by_role("button", name="添加").click()
            page.get_by_placeholder("学工号/注册手机号").click()
            page.get_by_placeholder("学工号/注册手机号").fill(self.__buddy)
            page.get_by_role("button", name="保存").click()
        else:
            print("Nice! You have friends to play with you!")

        page.wait_for_timeout(1000)
        context.close()

    def main(self, playwright: Playwright):
        self.__browser = playwright.chromium.launch(headless=self.__headless)
        date = datetime.today()
        delta_day = 2
        date += timedelta(days=delta_day)
        date = date.strftime('%m月%d日')

        self.__login()
        self.__buddy_check()

        if self.__snap_up_mode:
            now = datetime.now()
            seven_am = now.replace(hour=6, minute=59, second=00, microsecond=0)
            target = seven_am
            if now >= seven_am:
                target += timedelta(days=1)
            while now < target:
                now = datetime.now()
                time.sleep(5)
                print(now.strftime("%H:%M:%S"))

        print(f"You are ready to play on {date} at {self.__stadium_str}...")

        self.__date = date

        self.__login()

        res = self.__run()

        if not res:
            print("Unlucky! Play badminton in a few days!")
        else:
            print(f"Lucky you! Got {res}. Hurry up and pay for it!")

        self.__browser.close()
