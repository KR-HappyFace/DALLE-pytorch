# -*- coding:utf8 -*-
def remove_style(input_text: str) -> str:
    # split sentences by .
    sentences = input_text.split(".")
    return_sentences = []

    for sentence in sentences:
        if "스타일" in sentence:
            # remove the sentence from the list
            pass
        else:
            return_sentences.append(sentence)
            pass
    # join sentences into one str
    return ".".join(return_sentences).strip()


# text = "스타일에서 스타일은 리조트이다. 스타일에서 서브스타일은 모던이다. 원피스에서 기장은 미디이다. 원피스에서 색상은 와인이다. 원피스에서 카테고리는 드레스이다. 원피스에서 소매기장은 반팔이다. 원피스에서 소재에는 저지이다. 원피스에서 프린트에는 무지이다. 원피스에서 넥라인은 라운드넥이다. 원피스에서 핏은 루즈이다."
# print(remove_style(text))
# 원피스에서 기장은 미디이다. 원피스에서 색상은 와인이다. 원피스에서 카테고리는 드레스이다. 원피스에서 소매기장은 반팔이다. 원피스에서 소재에는 저지이다. 원피스에서 프린트에는 무지이다. 원피스에서 넥라인은 라운드넥이다. 원피스에서 핏은 루즈이다.
