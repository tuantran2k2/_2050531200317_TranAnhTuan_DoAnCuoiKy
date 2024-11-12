import re
from unstructured.cleaners.core import (
    group_broken_paragraphs,
    clean,
    group_broken_paragraphs,
)

unwanted_chars = [
    "ü",
    "ÿ",
    "þ",
    "®",
    "±",
    "©",
    "µ",
    "÷",
    "v ",
    "Ø",
    "€",
    "ƒ",
    "†",
    "‡",
    "ˆ",
    "Š",
    "Œ",
    "Ä",
    "•",
    "˜",
    "™",
    "š",
    "›",
    "œ",
    "ž",
    "Ÿ",
    "¡",
    "¢",
    "£",
    "¤",
    "¥",
    "¦",
    "§",
    "¨",
    "ª",
    "«",
    "¬",
    "°",
    "²",
    "³",
    "µ",
    "¶",
    "»",
    "¿",
    "Ä",
    "ü ",
    "ÿ ",
    "þ ",
    "® ",
    "± ",
    "© ",
    "µ ",
    "÷ ",
    "v ",
    "Ø ",
    "€ ",
    "ƒ ",
    "† ",
    "‡ ",
    "ˆ ",
    "Š ",
    "Œ ",
    "Ä ",
    "• ",
    "˜ ",
    "™ ",
    "š ",
    "› ",
    "œ ",
    "ž ",
    "Ÿ ",
    "¡ ",
    "¢ ",
    "£ ",
    "¤ ",
    "¥ ",
    "¦ ",
    "§ ",
    "¨ ",
    "ª ",
    "« ",
    "¬ ",
    "° ",
    "² ",
    "³ ",
    "µ ",
    "¶ ",
    "» ",
    "¿ ",
    "Ä ",
]


def clean_text(text, bullets):
    # Biểu thức chính quy để tìm các ký tự đầu dòng
    chars_pattern = "|".join(re.escape(char) for char in bullets)
    bullet_pattern = re.compile(
        r"((?:" + chars_pattern + r").+?)(?=(?:" + chars_pattern + r")|\Z)", re.DOTALL
    )

    # Tìm tất cả các đoạn văn bắt đầu bằng ký tự đầu dòng
    matches = bullet_pattern.findall(text)

    # Loại bỏ các ký tự xuống dòng không cần thiết trong mỗi đoạn văn
    cleaned_parts = []
    for match in matches:
        cleaned_part = " ".join(match.split())
        cleaned_parts.append(cleaned_part)

    # Tìm tất cả các đoạn văn không bắt đầu bằng ký tự đầu dòng
    other_parts = bullet_pattern.split(text)
    other_parts = [
        part
        for part in other_parts
        if part.strip() and not re.match(chars_pattern, part.strip())
    ]

    # Ghép tất cả các đoạn văn lại với nhau, mỗi đoạn một dấu xuống hàng
    cleaned_text = "\n\n".join(other_parts + cleaned_parts)
    return cleaned_text


def remove_specific_chars(text, chars):
    pattern = re.compile("|".join(re.escape(char) for char in chars))
    cleaned_text = pattern.sub("-", text)
    return cleaned_text


def remove_char_dots(text):
    text = re.sub(r"\n\s*\n", "\n\n", text)
    text = re.sub(
        r" {3,}", " ", text
    )  # Thay thế một hoặc nhiều dòng trắng bằng một dòng mới
    text = re.sub(r"\.\.\.", ".", text)  # Thay thế "..." bằng "."
    text = re.sub(r"\.\.\.", ".", text)  # Thay thế "..." bằng "."
    text = re.sub(r"\.\.\.", ".", text)  # Thay thế "..." bằng "."

    return text


def clean_data_optimized(texts):
    _texts = []
    for text in texts:
        text = re.sub(r"\n\s*\n", "\n", text)
        text = re.sub(r" {3,}", " ", text)
        text = re.sub(r"\.\.\.", ".", text)
        text = re.sub(r"\.\.\.", ".", text)
        text = re.sub(r"\.\.\.", ".", text)
        _texts.append(text)

    return _texts


def clean_data_unstructured(texts):
    _text = []
    for text in texts:
        # text = clean_text(text, unwanted_chars)
        text = remove_specific_chars(text, unwanted_chars)
        # text = clean(text, extra_whitespace=True, dashes=True, bullets=True, lowercase=False)
        text = group_broken_paragraphs(text)
        text = remove_char_dots(text)
        _text.append(text)
    return _text


# Fix mấy ngoặc nhọn với đồ trong string
def validate_and_fix_braces(text):
    text = str(text)
    # Định nghĩa các ký tự đặc biệt cần escape
    special_characters = {"{": "\\(", "}": "\\)", "]": "\\)", "[": "\\(", '"': "\\'"}
    # special_characters = {'{': '\\{', '}': '\\}', ']': '\\]', '[': '\\[', '"': '\\"', "'": "\\'"}

    # Thay thế từng ký tự đặc biệt trong chuỗi đầu vào
    for char, escape_char in special_characters.items():
        text = text.replace(char, escape_char)

    return text

    # return ''.join(result)


# Chuyển answer_keyword từ string sang mảng, loại bỏ từ Answer: và dấu "-" đầu dòng
def process_strings(input_string):
    if input_string.startswith("Answer:"):
        input_string = input_string.replace("Answer:", "").strip()
        if "- " in input_string:
            items = input_string.split("\n")
            result_array = [
                item.strip().lstrip("- ").strip() for item in items if item.strip()
            ]
        else:
            result_array = [input_string]
    else:
        result_array = [input_string]

    return result_array


def array_to_string(array):
    strings = "("
    for arr in array:
        strings += arr + ", "

    strings += ")"

    return strings


def process_string_json(string):
    # Tách chuỗi theo đoạn '```python' để lấy phần code
    parts = string.split("```json")
    # Kiểm tra và tách phần code bên trong nếu nó tồn tại
    if len(parts) > 1:
        string_code = parts[1].split("```")[0].strip()
    else:
        string_code = None
    return string_code
