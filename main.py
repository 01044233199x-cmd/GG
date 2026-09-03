# ==========================================
import os
import subprocess
import pydub

# 1~6번 음원 데이터셋 통합
def prepare_dataset(audio_files, output_dir="dataset"):
    os.makedirs(output_dir, exist_ok=True)
    combined = pydub.AudioSegment.empty()
    
    for file_path in audio_files:
        if os.path.exists(file_path):
            sound = pydub.AudioSegment.from_file(file_path)
            combined += sound
            
    output_path = os.path.join(output_dir, "combined_vocal.wav")
    combined.export(output_path, format="wav")
    print(f"[+] 데이터셋 통합 완료: {output_path}")
    return output_path

# 7번 음원 커버 변환 및 MR 합성
def generate_ai_cover(target_audio_path, model_path, output_path="output/final_cover.mp3"):
    os.makedirs("output", exist_ok=True)
    
    vocal_path = "output/vocal.wav"
    mr_path = "output/mr.wav"
    converted_vocal_path = "output/converted_vocal.wav"
    
    # Step 1: 음원 분리 (UVR5 CLI 실행 예시)
    subprocess.run(
        f"python -m uvr5.separate --input {target_audio_path} --out_vocal {vocal_path} --out_mr {mr_path}",
        shell=True
    )
    
    # Step 2: RVC 모델로 보컬 변환 (Voice Conversion)
    subprocess.run(
        f"python -m rvc.infer --model {model_path} --input {vocal_path} --output {converted_vocal_path}",
        shell=True
    )
    
    # Step 3: 변환된 보컬 + original MR 합성
    vocal = pydub.AudioSegment.from_file(converted_vocal_path)
    mr = pydub.AudioSegment.from_file(mr_path)
    
    final_cover = mr.overlay(vocal)
    final_cover.export(output_path, format="mp3")
    
    return output_path
