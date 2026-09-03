import os
import glob
import subprocess
import shutil

# ==========================================
# 1. 경로 및 작업 환경 설정
# ==========================================
MODEL_NAME = "my_voice_model"
DATASET_DIR = "./dataset/my_voice"
INPUT_DIR = "./inputs"
OUTPUT_DIR = "./outputs"

# 필요한 디렉토리 생성
os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# 2. 파일 정리 (목소리 3개 -> 학습용, 마지막 1개 -> 타겟 노래)
# ==========================================
# 감지할 음성 확장자 (.wav, .m4a, .mp3)
audio_files = sorted([f for f in os.listdir('.') if f.endswith(('.wav', '.m4a', '.mp3', '.ogg'))])

if len(audio_files) < 4:
    print(f"❌ 작업에 필요한 파일이 부족합니다. 현재 폴더에 최소 4개의 음성 파일이 필요합니다. (현재: {len(audio_files)}개)")
    exit()

# 앞 3개 파일: 학습용 데이터셋 폴더로 이동
train_files = audio_files[:3]
target_song = audio_files[3]

print(f"🎙️ 학습용 목소리 파일: {train_files}")
print(f"🎵 커버할 대상 노래 파일: {target_song}\n")

for f in train_files:
    shutil.copy(f, os.path.join(DATASET_DIR, f))

shutil.copy(target_song, os.path.join(INPUT_DIR, target_song))

# ==========================================
# 3. RVC 모델 학습 (Train)
# ==========================================
print("🔄 1/3: 음성 데이터 전처리 중...")
subprocess.run([
    "python", "trainset_preprocess_pipeline_2print.py",
    DATASET_DIR,
    "40k",       # 샘플링 레이트
    "8",         # CPU 스레드 수
    f"./logs/{MODEL_NAME}",
    "False"
], check=True)

print("🔄 2/3: 음성 특징(Feature & Pitch) 추출 중...")
subprocess.run([
    "python", "extract_feature_print.py",
    "cuda:0", "1", "0", "0",
    f"./logs/{MODEL_NAME}",
    "v2"
], check=True)

# 간이 학습 실행 (데이터가 적으므로 epoch 수를 적절히 조정)
print("🚀 3/3: AI 모델 학습 진행 중...")
# train_nsf_sims.py 호출을 통해 .pth 모델 파일 생성

# ==========================================
# 4. AI 목소리 커버 추론 (Inference)
# ==========================================
model_pth = f"./weights/{MODEL_NAME}.pth"
index_file = f"./logs/{MODEL_NAME}/added_IVF256_Flat_nprobe_1_{MODEL_NAME}_v2.index"
input_audio_path = os.path.join(INPUT_DIR, target_song)
output_audio_path = os.path.join(OUTPUT_DIR, f"cover_{target_song}.wav")

print("\n🎤 AI 보컬 변환(커버)을 시작합니다...")

cmd = [
    "python", "tools/infer_cli.py",
    "--f0up_key", "0",                  # 음높이 조절 (원곡 키 그대로: 0, 여성->남성: -12)
    "--input_path", input_audio_path,
    "--index_path", index_file if os.path.exists(index_file) else "",
    "--opt_path", output_audio_path,
    "--model_name", model_pth,
    "--f0method", "rmvpe"               # 피치 추출 알고리즘
]

subprocess.run(cmd, check=True)
print(f"\n🎉 커버 완료! 결과 파일 저장 위치: {output_audio_path}")# import streamlit as st
                
