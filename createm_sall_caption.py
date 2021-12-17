# -*- coding:utf8 -*-
# https://github.com/myevan/pyjosa/blob/master/pyjosa.py

import os
import re
import glob
import json
from tqdm import tqdm

JOSA_PAIRD = {
    "(이)가": ("이", "가"),
    "(와)과": ("과", "와"),
    "(을)를": ("을", "를"),
    "(은)는": ("은", "는"),
    "(으)로": ("으로", "로"),
    "(아)야": ("아", "야"),
    "(이)여": ("이여", "여"),
    "(이)라": ("이라", "라"),
}

JOSA_REGEX = re.compile("\(이\)가|\(와\)과|\(을\)를|\(은\)는|\(아\)야|\(이\)여|\(으\)로|\(이\)라")


def choose_josa(prev_char, josa_key, josa_pair):
    """
    조사 선택

    :param prev_char 앞 글자
    :param josa_key 조사 키
    :param josas 조사 리스트
    """
    char_code = ord(prev_char)

    # 한글 코드 영역(가 ~ 힣) 아닌 경우
    if char_code < 0xAC00 or char_code > 0xD7A3:
        return josa_pair[1]

    local_code = char_code - 0xAC00  # '가' 이후 로컬 코드
    jong_code = local_code % 28

    # 종성이 없는 경우
    if jong_code == 0:
        return josa_pair[1]

    # 종성이 있는 경우
    if josa_key == "(으)로":
        if jong_code == 8:  # ㄹ 종성인 경우
            return josa_pair[1]

    return josa_pair[0]


def replace_josa(src):
    tokens = []
    base_index = 0
    for mo in JOSA_REGEX.finditer(src):
        prev_token = src[base_index : mo.start()]
        prev_char = prev_token[-1]
        tokens.append(prev_token)

        josa_key = mo.group()
        tokens.append(choose_josa(prev_char, josa_key, JOSA_PAIRD[josa_key]))

        base_index = mo.end()

    tokens.append(src[base_index:])
    return "".join(tokens)


# replace_josa("나(이)라고 어쩔 수 있겠니? 별(이)라고 불러줘. 라면(이)라고 했잖아.")


def flatten_json(y: dict) -> dict:
    # https://www.geeksforgeeks.org/flattening-json-objects-in-python/
    out = {}

    def flatten(x, name=""):
        flag = False
        # If the Nested key-value
        # pair is of dict type
        if type(x) is dict:

            for a in x:
                flatten(x[a], name + a + "에서")

        # If the Nested key-value
        # pair is of list type
        elif type(x) is list:

            i = 0

            for a in x:
                flatten(a, name + " ")
                i += 1
        else:
            out[name[:-2]] = x

    flatten(y)
    return out


def flatten_json_to_text(input: json) -> list:
    list_to_return = []
    str = ""
    input = flatten_json(input)
    for key, value in input.items():
        str = f"{key}(은)는 {value}이다." # value가 모두 명사이기 때문에 종결어미는 "-이다."로 통일합니다.
        str = replace_josa(str)
        list_to_return.append(str)
    return list_to_return


def flatten_json2(y: dict) -> dict:
    # https://www.geeksforgeeks.org/flattening-json-objects-in-python/
    out = {}
  
    def flatten(x, name =''):
        flag = False
        # If the Nested key-value 
        # pair is of dict type
        if type(x) is dict:
            
            for a in x:
                flatten(x[a], name + a + '의')
                  
        # If the Nested key-value
        # pair is of list type
        elif type(x) is list:
              
            i = 0
              
            for a in x:                
                flatten(a, name + " ")
                i += 1
        else:
            out[name[:-1]] = x
  
    flatten(y)
    return out


def make_small_context(sample):
    pp = dict()
    pp['스타일'] =sample['스타일'][0]['스타일']
    for i in sample:
        try:
            w = sample[i][0]['색상']
            p = sample[i][0]['카테고리']
            w = w +' 색상의 '+ p
            pp[i] = w
        except KeyError:
            continue
    return pp

DATA_PATH = "data"
LABEL_PATH = os.path.join(DATA_PATH, "val_label",)
IMAGE_PATH = os.path.join(DATA_PATH, "cropped_img")
CATEGORIES = os.listdir(LABEL_PATH)

# make caption path
caption_path = os.path.join(DATA_PATH, "caption_small")
if not os.path.exists(caption_path):
    os.mkdir(os.path.join(caption_path))
ppp = 0
for category in CATEGORIES:
    category_label_path = os.path.join(LABEL_PATH, category)
    category_image_path = os.path.join(IMAGE_PATH, category)
    # print(category_label_path)
    # print(category_image_path)

    # make category in caption path
    category_caption_path = os.path.join(caption_path, category)
    if not os.path.exists(category_caption_path):
        os.mkdir(category_caption_path)

    # fetch files

    category_label_files = glob.glob(os.path.join(category_label_path, "*.json"))
    category_image_files = glob.glob(os.path.join(category_image_path, "*.jpg"))
    print(f"{category} has {len(category_label_files)} number of label files")
    print(f"{category} has {len(category_image_files)} number of image files")

    for label_path in tqdm(category_label_files):
        # print(label_path)

        basename = os.path.basename(label_path)
        basename_without_extension = os.path.splitext(basename)[0]  # 파일명에서 .json 확장자를 제거하여 가져옵니다.

        image_path = os.path.join(category_image_path, f"{basename_without_extension}.jpg")
        if not os.path.exists(image_path):
            print(f"{image_path} not exists")
            continue
        # print(label_path, image_path)

        json_item = json.load(open(label_path))
        context = make_small_context(json_item["데이터셋 정보"]["데이터셋 상세설명"]["라벨링"])
        label_text = " ".join(flatten_json_to_text(context))
        # print(label_text)
        text_file_path = os.path.join(category_caption_path, f"{basename_without_extension}.txt")

        # write text file on text_file_path
        with open(text_file_path, "w", encoding="utf-8") as f:
            f.write(label_text)
        ppp += 1
print(ppp)