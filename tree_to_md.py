import os
import re

def starts_with_digit(s):
    pattern = r'^\d'
    return bool(re.match(pattern,s))

# 현재 작업 디렉토리를 기준으로 한 상대 경로 추출
def relative_path_from_cwd(path):
    s_path = re.sub(r'\s', '%20', os.path.relpath(path))
    s_path = re.sub(r'\\', '/', s_path)
    return s_path

def generate_markdown_tree(root_dir, depth=0):
    markdown_tree = ""
    indent = "  " * depth

    for item in sorted(os.listdir(root_dir)):
        # 현재 아이템의 전체 경로

        # 숫자로(규칙대로) 명명되지 않은 폴더는 제외
        if depth == 0 and not starts_with_digit(item):
            continue

        item_path = os.path.join(root_dir, item)
        r_item_path = relative_path_from_cwd(item_path)

        # 디렉토리인 경우
        if os.path.isdir(item_path):
            # 디렉토리 이름을 마크다운에 추가
            markdown_tree += f"{indent}- {item}\n"
            # 해당 디렉토리의 내용을 재귀적으로 처리
            markdown_tree += generate_markdown_tree(item_path, depth + 1)
        # 파일인 경우
        elif os.path.isfile(item_path):
            # 파일 이름을 마크다운에 추가
            markdown_tree += f"{indent}- [{item}]({r_item_path})\n"

    return markdown_tree

# 폴더 경로
current_dir = os.path.dirname(__file__)
folder_path = os.path.abspath(os.path.join(current_dir, r"..\CS_STUDY"))

# 폴더 구조를 마크다운 형식으로 변환
markdown_text = generate_markdown_tree(folder_path)

# 변환된 마크다운 출력
print(markdown_text)
