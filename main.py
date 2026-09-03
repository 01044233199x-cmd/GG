# 1. 필수 라이브러리 및 RVC 모듈 설치
!git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
%cd Retrieval-based-Voice-Conversion-WebUI
!pip install -r requirements.txt

# 2. 데이터셋 디렉토리 생성 및 음성 파일 배치
import os

dataset_path = "./dataset/my_voice"
os.makedirs(dataset_path, exist_ok=True)

print("준비한 .wav 파일들을 './dataset/my_voice' 폴더에 업로드하세요.")
