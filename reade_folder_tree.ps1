# 사용자로부터 폴더 경로 입력 받기
$folderPath = Read-Host "폴더 경로를 입력하세요 (예: C:\Users\Username\Project)"

# README.md 파일 생성 및 제목 및 설명 추가
echo "# 폴더 구조" | Out-File -FilePath README.md -Encoding utf8
echo "아래는 프로젝트의 폴더 구조를 나타냅니다." | Out-File -FilePath README.md -Encoding utf8 -Append

# 입력받은 폴더 경로의 폴더 및 파일 구조를 트리 형식으로 출력하고 README.md에 추가
tree $folderPath /F | Out-File -FilePath foldertree.md -Encoding utf8 -Append