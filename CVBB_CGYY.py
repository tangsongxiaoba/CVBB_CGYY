import time
from datetime import datetime, timedelta

import requests, json, re
from playwright.sync_api import Playwright, sync_playwright

class CVBB_CGYY:
    def __init__(self, stu_id, stu_pwd, prior_list, verify_usr, verify_pwd, verify_sid, snap_up_mode=True):
        self.stu_id = stu_id
        self.stu_pwd = stu_pwd
        self.prior_list = prior_list
        self.verify_usr = verify_usr
        self.verify_pwd = verify_pwd
        self.verify_sid = verify_sid
        self.snap_up_mode = snap_up_mode

    def decode(self, img):  # Powered by xxk!
        img = img.strip()

        # 如果 base64 数据的长度不是 4 的倍数，补充 '='
        missing_padding = len(img) % 4
        if missing_padding != 0:
            img += '=' * (4 - missing_padding)

        data = {
            "user": self.verify_usr,
            "pass2": self.verify_pwd,  # 使用MD5加密后的密码
            "softid": self.verify_sid,
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

    def run(self, playwright: Playwright) -> None:

        date = datetime.today()
        delta_day = 2
        date += timedelta(days=delta_day)
        date = date.strftime('%m月%d日')

        if self.snap_up_mode:
            now = datetime.now()
            seven_am = now.replace(hour=6, minute=59, second=30, microsecond=0)
            target = seven_am
            if now >= seven_am:
                target += timedelta(days=1)
            while now < target:
                now = datetime.now()
                time.sleep(5)
                print(now.strftime("%H:%M:%S"))

        print(f"You are ready to play on {date}...")
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://sso.buaa.edu.cn/login?service=https://cgyy.buaa.edu.cn/venue-server/sso/manageLogin")
        page.locator("#loginIframe").content_frame.get_by_role("textbox", name="请输入学工号").click()
        page.locator("#loginIframe").content_frame.get_by_role("textbox", name="请输入学工号").fill(self.stu_id)
        page.locator("#loginIframe").content_frame.get_by_placeholder("请输入密码").click()
        page.locator("#loginIframe").content_frame.get_by_placeholder("请输入密码").fill(self.stu_pwd)
        page.locator("#loginIframe").content_frame.get_by_role("button", name="登录").click()
        page.wait_for_timeout(10000)
        page.goto("https://cgyy.buaa.edu.cn/venue/venue-reservation/57") # Currently only support for main stadium

        succeeded = False

        if self.snap_up_mode:
            now = datetime.now()
            seven_am = now.replace(hour=7, minute=0, second=2, microsecond=0)
            while now < seven_am:
                now = datetime.now()

        for tu in self.prior_list:
            reserved = []
            page.reload()
            try:
                page.get_by_role("button", name="关闭").click(timeout=3000)
            except TimeoutError as e:
                print(f"Error encountered: {e}. May be the pop-up no longer exists...")
            page.get_by_text(date).click()
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
                for i in range(1, cells.count() - 1): # no No.1 court for its obstacle
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
                exit(-1) # expected to support for adding buddies automatically
            buddy.click()

            btn = page.locator("div.submit_order_box.pc div.action div:nth-child(2)")
            if "disab" in btn.get_attribute("class"):
                print("I can't press the submit button! Check out the website for reason...")
                exit(-1) # expected to solve for other things...
            btn.click()

            # solve verify code
            img = page.locator("div.mask div.verifybox div.verifybox-bottom \
                                div div.verify-img-out div.verify-img-panel img")
            img_base64 = img.get_attribute("src").split(',')[1]
            text = page.locator("div.mask div.verifybox div.verifybox-bottom \
                                div div.verify-bar-area").text_content()
            text = re.search(r'【(.*?)】', text).group(1).split(',')
            position = self.decode(img_base64)
            bbox = img.bounding_box()

            for t in text:
                x_offset = bbox['x'] + int(position[t][0])
                y_offset = bbox['y'] + int(position[t][1])
                page.mouse.click(x_offset, y_offset)
                page.wait_for_timeout(500)

            succeeded = True
            break

        if not succeeded:
            print("Unlucky! Play badminton tommorrow!")
        else:
            print("Lucky you! Have fun with your friends!")

        context.close()
        browser.close()


with sync_playwright() as pw:

    # 验证码识别平台账密
    cjy_usr = ""
    cjy_pwd = ""
    cjy_sid = ""

    # 校园账户密码
    student_id = ""
    student_pwd = ""

    # 期望时间
    p_list = [('16:00-17:00', '17:00-18:00'), ('20:00-21:00', '21:00-22:00')]
    cgyy = CVBB_CGYY(student_id, student_pwd, p_list, cjy_usr, cjy_pwd, cjy_sid, True)
    cgyy.run(pw)
