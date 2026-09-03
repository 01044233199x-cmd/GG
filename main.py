# import streamlit as st
import os
import subprocess

# 페이지 기본 설정
st.set_page_config(page_title="AI Voice Cover Studio", page_icon="🎤", layout="centered")

st.title("🎤 AI Voice Cover Studio")
st.write("학습된 목소리 모델을 선택하고, 변환할 보컬 음성을 업로드하세요!")

# 1. 모델 파일(.pth) 목록 가져오기
weights_dir = "./weights"
os.makedirs(weights_dir, exist_ok=True)
os.makedirs("./inputs", exist_ok=True)
os.makedirs("./outputs", exist_ok=True)

model_files = [f for f in os.listdir(weights_dir) if f.endswith(".pth")]

# 2. 사이드바 - 모델 및 설정을 위한 인터페이스
st.sidebar.header("⚙️ 변환 설정")
selected_model = st.sidebar.selectbox("사용할 음성 모델 선택", model_files if model_files else ["모델 없음"])
pitch_shift = st.sidebar.slider("음고(Pitch) 조절", min_value=-12, max_value=12, value=0, help="남성->여성: +12 / 여성->남성: -12")

# 3. 메인 - 음성 파일 업로드
uploaded_file = st.file_uploader("커버할 노래의 보컬 트랙(.wav, .mp3)을 업로드하세요", type=["wav", "mp3"])

if uploaded_file is not None:
    # 업로드한 파일 저장
    input_path = os.path.join("./inputs", uploaded_file.name)
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.audio(input_path, format="audio/wav")
    st.success(f"파일 업로드 완료: {uploaded_file.name}")

    # 4. 변환 실행 버튼
    if st.button("🚀 AI 목소리로 변환하기"):
        if not model_files or selected_model == "모델 없음":
            st.error("./weights 폴더에 학습된 .pth 모델 파일을 넣어주세요!")
        else:
            output_path = os.path.join("./outputs", f"converted_{uploaded_file.name}")
            model_path = os.path.join(weights_dir, selected_model)
            
            with st.spinner("AI가 목소리를 변환하고 있습니다. 잠시만 기다려주세요..."):
                # RVC CLI 추론 명령어 실행
                cmd = [
                    "python", "tools/infer_cli.py",
                    "--f0up_key", str(pitch_shift),
                    "--input_path", input_path,
                    "--opt_path", output_path,
                    "--model_name", model_path,
                    "--f0method", "rmvpe"
                ]
                
                try:
                    subprocess.run(cmd, check=True)
                    st.success("🎉 변환이 완료되었습니다!")
                    
                    # 결과 오디오 재생 및 다운로드
                    st.audio(output_path, format="audio/wav")
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="⬇️ 변환된 음성 다운로드",
                            data=file,
                            file_name=f"cover_{uploaded_file.name}",
                            mime="audio/wav"
                        )
                except Exception as e:
                    st.error(f"변환 중 오류가 발생했습니다: {e}")
