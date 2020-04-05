from django.test import TestCase
from sign.models import Event, Guest
from django.contrib.auth.models import User


class ModelTest(TestCase):
    """针对模型的测试用例"""
    def setUp(self):
        """造数据"""
        Event.objects.create(id=3, name="苹果", status=True, limit=4, address="深圳", start_time="2019-12-20 09:35:00")
        Guest.objects.create(id=7, event_id=3, realname="小蓝", phone="15359373846", email="983@qq.com", sign=False)

    def test_event_models(self):
        """测试event表确实造了这个数据"""
        result = Event.objects.get(name="苹果")
        self.assertEqual(result.address, "深圳")
        self.assertTrue(result.status)

    def test_guest_models(self):
        """测试guest表确实造了这个数据"""
        result = Guest.objects.get(phone="15359373846")
        self.assertEqual(result.realname, "小蓝")
        self.assertFalse(result.sign)


class IndexPageTest(TestCase):
    """index视图的测试用例"""
    def test_index_page_renders_index_template(self):
        """测试可以正常登录首页"""
        response = self.client.get("/index/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")


class LoginActionTest(TestCase):
    """测试登录动作"""
    def setUp(self):
        User.objects.create_user("admin", "admin@qq.com", "admin123456")

    def test_add_admin(self):
        """测试添加用户"""
        user = User.objects.get(username='admin')
        self.assertEqual(user.username, "admin")
        self.assertEqual(user.email, "admin@qq.com")

    def test_login_action_username_password_null(self):
        """用户密码为空"""
        test_data = {"username": "", "password": ""}
        response = self.client.post("/login_action/", data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"username or password error!", response.content)

    def test_login_action_username_password_error(self):
        """测试用户密码错误"""
        test_data = {"username": "abc", "password": "123"}
        response = self.client.post("/login_action/", data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"username or password error!", response.content)

    def test_login_action_success(self):
        """测试登录成功"""
        test_data = {"username": "admin", "password": "admin123456"}
        response = self.client.post("/login_action/", data=test_data)
        self.assertEqual(response.status_code, 301)


class EventManageTest(TestCase):
    """发布会管理模块测试"""

    def setUp(self):
        User.objects.create_user("admin_one", "admin_one@qq.com", "admin123456")
        Event.objects.create(id=4, name="huawei", status=True, limit=5, address="shenzhen", start_time="2019-12-20 09:35:00")
        self.login_user = {"username": "admin_one",
                           "password": "admin123456", }
        # 登录
        self.client.post("/login_action/", data=self.login_user)

    def test_event_manage_success(self):
        """测试发布会"""
        # 发布会页面的请求
        response = self.client.post("/event_manage/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"huawei", response.content)
        self.assertIn(b"shenzhen", response.content)

    def test_event_manage_search_success(self):
        """测试发布会搜索"""
        # 发布会页面的搜索请求
        response = self.client.post("/search_event_name/", {"name": "huawei", })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"huawei", response.content)
        self.assertIn(b"shenzhen", response.content)


class GuestManageTest(TestCase):
    """嘉宾管理模块测试"""
    def setUp(self):
        User.objects.create_user("admin_two", "admin_two@qq.com", "admin123456")
        Event.objects.create(id=5, name="xiaomi", status=True, limit=5, address="shenzhen", start_time="2019-12-20 09:35:00")
        Guest.objects.create(id=8, event_id=5, realname="xiaozheng", phone="15359373847", email="983@qq.com", sign=False)
        self.login_user = {"username": "admin_two",
                           "password": "admin123456", }
        # 登录
        self.client.post("/login_action/", data=self.login_user)

    def test_guest_manage_success(self):
        """测试嘉宾信息"""
        # 嘉宾页面请求
        response = self.client.post("/guest_manage/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"15359373847", response.content)
        self.assertIn(b"xiaozheng", response.content)

    def test_guest_manage_search_success(self):
        """测试嘉宾页面搜索功能"""
        # 嘉宾页面搜索功能请求
        response = self.client.post("/search_guest_name/", {"phone": "15359373847", })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"xiaozheng", response.content)
        self.assertIn(b"15359373847", response.content)


class SignIndexActionTest(TestCase):
    """发布会签到功能测试"""
    def setUp(self):
        User.objects.create_user("admin_three", "admin_three@qq.com", "admin123456")
        Event.objects.create(id=1, name="meizu", status=1, limit=5, address="shenzhen", start_time="2019-12-20 09:35:00")
        Event.objects.create(id=2, name="jinli", status=1, limit=5, address="shenzhen", start_time="2019-12-20 09:35:00")
        Guest.objects.create(id=1, event_id=1, realname="xiaowang", phone="15359373849", email="983@qq.com", sign=0)
        Guest.objects.create(id=2, event_id=2, realname="xiaosong", phone="15359373840", email="983@qq.com", sign=1)
        self.login_user = {"username": "admin_three",
                           "password": "admin123456", }

    def test_sign_index_action_phone_null(self):
        """手机号为空时"""
        response = self.client.post("/sign_index_action/1/", {"phone": "", })
        # 疑问这里为什么是302？？在页面中通过开发者工具看到的却是200
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Phone number does not exist", response.content)

    def test_sign_index_action_phone_or_event_id_error(self):
        """手机号或者发布会id错误时"""
        # 手机号错误
        response = self.client.post("/sign_index_action/2/", {"phone": "15359373849", })
        # 疑问这里为什么是302？？在页面中通过开发者工具看到的却是200
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"There is no corresponding mobile number for this conference", response.content)

    def test_sign_index_action_user_sign_has(self):
        """用户已签到时"""
        response = self.client.post("/sign_index_action/2/", {"phone": "15359373840", })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"You've signed in", response.content)

    def test_sign_index_action_user_sign_success(self):
        """用户签到成功时"""
        response = self.client.post("/sign_index_action/1/", {"phone": "15359373849", })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sign in successfully", response.content)
