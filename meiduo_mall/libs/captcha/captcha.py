#!/usr/bin/env python
# -*- coding: utf-8 -*-

# refer to `https://bitbucket.org/akorn/wheezy.captcha`

import random
import math
import os.path
from io import BytesIO

from PIL import Image
from PIL import ImageFilter
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype


class Bezier:
    def __init__(self):
        self.tsequence = tuple([t / 20.0 for t in range(21)])
        self.beziers = {}

    def pascal_row(self, n):
        """ Returns n-th row of Pascal's triangle
        """
        result = [1]
        x, numerator = 1, n
        for denominator in range(1, n // 2 + 1):
            x *= numerator
            x /= denominator
            result.append(x)
            numerator -= 1
        if n & 1 == 0:
            result.extend(reversed(result[:-1]))
        else:
            result.extend(reversed(result))
        return result

    def make_bezier(self, n):
        """ Bezier curves:
            http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
        """
        try:
            return self.beziers[n]
        except KeyError:
            combinations = self.pascal_row(n - 1)
            result = []
            for t in self.tsequence:
                tpowers = (t ** i for i in range(n))
                upowers = ((1 - t) ** i for i in range(n - 1, -1, -1))
                coefs = [c * a * b for c, a, b in zip(combinations,
                                                      tpowers, upowers)]
                result.append(coefs)
            self.beziers[n] = result
            return result


class Captcha(object):
    def __init__(self):
        self._bezier = Bezier()
        self._dir = os.path.dirname(__file__)
        # self._captcha_path = os.path.join(self._dir, '..', 'static', 'captcha')

    @staticmethod
    def instance():
        if not hasattr(Captcha, "_instance"):
            Captcha._instance = Captcha()
        return Captcha._instance

    def initialize(self, width=220, height=80, color=None, text=None, fonts=None):
        # Avoid look-alike characters such as O/0, I/1, S/5, Z/2 and G/6.
        alphabet = 'ABCDEFGHJKLMNPQRTUVWXY3479'
        self._text = text if text else random.sample(alphabet, 4)
        self.fonts = fonts if fonts else [os.path.join(self._dir, 'fonts', 'actionj.ttf')]
        self.width = width
        self.height = height
        self._color = color if color else (24, 55, 92)

    @staticmethod
    def random_color(start, end, opacity=None):
        red = random.randint(start, end)
        green = random.randint(start, end)
        blue = random.randint(start, end)
        if opacity is None:
            return red, green, blue
        return red, green, blue, opacity

    # draw image

    def background(self, image):
        Draw(image).rectangle([(0, 0), image.size], fill=self.random_color(238, 255))
        return image

    @staticmethod
    def smooth(image):
        return image.filter(ImageFilter.SMOOTH)

    def curve(self, image, width=4, number=6, color=None):
        dx, height = image.size
        dx /= number
        path = [(dx * i, random.randint(0, height))
                for i in range(1, number)]
        bcoefs = self._bezier.make_bezier(number - 1)
        points = []
        for coefs in bcoefs:
            points.append(tuple(sum([coef * p for coef, p in zip(coefs, ps)])
                                for ps in zip(*path)))
        Draw(image).line(points, fill=color if color else self._color, width=width)
        return image

    def noise(self, image, number=50, level=2, color=None):
        width, height = image.size
        dx = width / 10
        width -= dx
        dy = height / 10
        height -= dy
        draw = Draw(image)
        for i in range(number):
            x = int(random.uniform(dx, width))
            y = int(random.uniform(dy, height))
            draw.line(((x, y), (x + level, y)), fill=color if color else self._color, width=level)
        return image

    def text(self, image, fonts, font_sizes=None, color=None):
        colors = (color,) if color else (
            (22, 55, 96), (76, 39, 96), (24, 92, 78), (112, 54, 28),
        )
        sizes = font_sizes or (52, 56, 60)
        width, height = image.size
        glyphs = []
        for char in self._text:
            font = truetype(random.choice(fonts), random.choice(sizes))
            bbox = font.getbbox(char)
            padding = 6
            glyph = Image.new(
                'RGBA',
                (bbox[2] - bbox[0] + padding * 2, bbox[3] - bbox[1] + padding * 2),
                (0, 0, 0, 0),
            )
            stroke_width = random.choice((0, 0, 1))
            glyph_color = random.choice(colors)
            outline_color = tuple(int(channel * 0.65 + 255 * 0.35) for channel in glyph_color)
            text_position = (padding - bbox[0], padding - bbox[1])
            draw = Draw(glyph)
            draw.text(text_position, char, font=font,
                      fill=(*outline_color, 255), stroke_width=2,
                      stroke_fill=(*outline_color, 255))
            draw.text(text_position, char, font=font,
                      fill=(*glyph_color, 255), stroke_width=stroke_width,
                      stroke_fill=(*glyph_color, 255))

            shadow_alpha = glyph.getchannel('A').filter(ImageFilter.GaussianBlur(radius=0.8))
            shadow_alpha = shadow_alpha.point(lambda alpha: int(alpha * 0.55))
            shadow = Image.new('RGBA', glyph.size, (30, 35, 50, 0))
            shadow.putalpha(shadow_alpha)
            layered_glyph = Image.new('RGBA', glyph.size, (0, 0, 0, 0))
            layered_glyph.alpha_composite(shadow, dest=(2, 2))
            layered_glyph.alpha_composite(glyph)
            glyph = layered_glyph
            glyph = self.distort_glyph(glyph)
            angle = random.uniform(-13, 13)
            glyph = glyph.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
            glyphs.append(glyph)

        gap = random.randint(8, 12)
        max_text_width = width - 24
        text_width = sum(glyph.width for glyph in glyphs) + gap * (len(glyphs) - 1)
        if text_width > max_text_width:
            scale = (max_text_width - gap * (len(glyphs) - 1)) / sum(glyph.width for glyph in glyphs)
            glyphs = [glyph.resize((int(glyph.width * scale), int(glyph.height * scale)),
                                   Image.Resampling.LANCZOS) for glyph in glyphs]
            text_width = sum(glyph.width for glyph in glyphs) + gap * (len(glyphs) - 1)

        offset = (width - text_width) // 2
        for glyph in glyphs:
            y = (height - glyph.height) // 2 + random.randint(-7, 7)
            image.paste(glyph, (offset, y), glyph)
            offset += glyph.width + gap

        return image

    @staticmethod
    def distort_glyph(glyph):
        """Bend strokes slightly with a smooth horizontal wave per scanline."""
        width, height = glyph.size
        amplitude = random.randint(2, 4)
        phase = random.uniform(0, 2 * math.pi)
        distorted = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        for y in range(height):
            shift = round(amplitude * math.sin(2 * math.pi * y / max(1, height - 1) + phase))
            row = glyph.crop((0, y, width, y + 1))
            distorted.paste(row, (shift, y), row)
        return distorted

    # draw text
    @staticmethod
    def warp(image, dx_factor=0.27, dy_factor=0.21):
        width, height = image.size
        dx = width * dx_factor
        dy = height * dy_factor
        x1 = int(random.uniform(-dx, dx))
        y1 = int(random.uniform(-dy, dy))
        x2 = int(random.uniform(-dx, dx))
        y2 = int(random.uniform(-dy, dy))
        image2 = Image.new('RGB',
                           (width + abs(x1) + abs(x2),
                            height + abs(y1) + abs(y2)))
        image2.paste(image, (abs(x1), abs(y1)))
        width2, height2 = image2.size
        return image2.transform(
            (width, height), Image.QUAD,
            (x1, y1,
             -x1, height2 - y2,
             width2 + x2, height2 + y2,
             width2 - x2, -y1))

    @staticmethod
    def offset(image, dx_factor=0.1, dy_factor=0.2):
        width, height = image.size
        dx = int(random.random() * width * dx_factor)
        dy = int(random.random() * height * dy_factor)
        image2 = Image.new('RGB', (width + dx, height + dy))
        image2.paste(image, (dx, dy))
        return image2

    @staticmethod
    def rotate(image, angle=25):
        return image.rotate(
            random.uniform(-angle, angle), Image.BILINEAR, expand=1)

    def captcha(self, path=None, fmt='JPEG'):
        """Create a captcha.

        Args:
            path: save path, default None.
            fmt: image format, PNG / JPEG.
        Returns:
            A tuple, (text, StringIO.value).
            For example:
                ('JGW9', '\x89PNG\r\n\x1a\n\x00\x00\x00\r...')

        """
        image = Image.new('RGB', (self.width, self.height), (248, 250, 253))
        image = self.background(image)
        image = self.noise(image, number=42, level=2, color=(202, 213, 226))
        image = self.curve(image, width=2, number=6, color=(163, 179, 198))
        image = self.curve(image, width=1, number=6, color=(190, 201, 216))
        image = self.text(image, self.fonts, font_sizes=(52, 56, 60))
        image = image.filter(ImageFilter.GaussianBlur(radius=0.55))
        text = "".join(self._text)
        out = BytesIO()
        image.save(out, format=fmt)
        return text, out.getvalue()

    def generate_captcha(self):
        self.initialize()
        return self.captcha("", fmt='PNG')

captcha = Captcha.instance()

if __name__ == '__main__':
    print(captcha.generate_captcha())
