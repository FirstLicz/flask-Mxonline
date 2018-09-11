from PIL import Image, ImageDraw, ImageFont, ImageFilter
from string import ascii_uppercase, ascii_lowercase
from random import randint
import os

from config import basedir


class CaptchaImage():
    """
        生成验证码图片
    """

    def __init__(self, length=4, operator=False, width=100, height=30):
        self.length = length
        self.operator = operator
        self.width = width
        self.height = height
        self.character_seed = ascii_lowercase + '0123456789' + ascii_uppercase
        self.font = os.path.join(basedir, 'app', 'static', 'fonts', 'SIMYOU.TTF')

    def generate_code(self):
        code = ''
        for num in range(self.length):
            index = randint(0, len(self.character_seed) - 1)
            code += self.character_seed[index] + ' '
        return code.rstrip()

    def generate_code_image(self):
        code = self.generate_code()
        img = Image.new('RGBA', size=(self.width, self.height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(self.font, 22)
        draw.text(
            xy=(self.width // len(code), 5),
            text=code,
            font=font,
            fill=(0, 0, 0)
        )
        # 划几根干扰线
        for num in range(randint(0, self.length)):
            x1 = randint(0, self.width // 3)
            y1 = randint(0, self.height // 3)
            x2 = randint(self.width // 3, self.width)
            y2 = randint(self.height // 3, self.height)
            draw.line(((x1, y1), (x2, y2)), fill='black', width=1)

        # 模糊下,加个滤镜
        img.filter(ImageFilter.FIND_EDGES)
        return img, code.replace(' ', '')


if __name__ == '__main__':
    captcha = CaptchaImage()
    # t = captcha.generate_code_image()
    print(captcha.font)
