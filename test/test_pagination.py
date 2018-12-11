import unittest

from app.models import User
from app import create_app
from app.utils.utils import Pagination


class TestPagination(unittest.TestCase):

    def setUp(self):  # 每个测试用例执行之前做操作
        self.app = create_app('development')
        self.app_context = self.app.app_context()
        self.app_context.push()
        print("生成实例之前")

    def tearDown(self):  # 每个测试用例执行之后做操作
        self.app_context.pop()
        print("生成实例之后")

    @classmethod
    def setUpClass(cls):  # 必须使用@classmethod 装饰器,所有test运行前运行一次
        pass

    @classmethod
    def tearDownClass(cls):  # 必须使用@classmethod 装饰器, 所有test运行完后运行一次
        pass

    def test_pagination(self):
        user = User.query.get_or_404(2)
        total_courses = user.courses
        a = Pagination(page=2, per_page=8, items=total_courses)
        print(a.get_items)
        self.assertTrue(a.has_prev)
        self.assertFalse(a.has_next)

    def test_page(self):
        user = User.query.get_or_404(2)
        total_courses = user.courses
        a = Pagination(page=1, per_page=8, items=total_courses)
        print(a.get_items)
        self.assertTrue(a.has_next)
        self.assertFalse(a.has_prev)


if __name__ == '__main__':
    unittest.main()  # 运行所有的测试用例
