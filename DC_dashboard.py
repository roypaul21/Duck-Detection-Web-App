import streamlit as st
import cv2
import requests
from streamlit_lottie import st_lottie
import streamlit.components.v1 as components
from streamlit_webrtc import webrtc_streamer
import tempfile
import os
import subprocess
from subprocess import Popen
import moviepy
import json
from moviepy.editor import VideoFileClip
import csv
import pandas as pd


class DuckCounting():

    def __init__(self, load_anim):

        # Load animation 
        def load_animurl(url):
            r = requests.get(url)
            if r.status_code != 200:
                return None
            else:
                return r.json()   
        
        #Detection Yolo Function
        def DetectYolo(self, filename, conf_thresh):
            count_dict = {"Pekin": [], "Pateros": [], "Muscovy": [], "Indian Runner": [], "Khaki Campbell": [], "Tsaiya": []}
            AverageCount_dict = {"Pekin": [], "Pateros": [], "Muscovy": [], "Indian Runner": [], "Khaki Campbell": [], "Tsaiya": [], "Total Count": []}

            process = Popen(["python", "YOLOv7_Model/detectyolo.py", '--source', f"{filename}", "--weights","best.pt", "--conf", f"{conf_thresh}"], stdout=subprocess.PIPE, shell=True)
            output, _ = process.communicate()
            process.wait() 
            print("-----Done Count Process-----")
            with open('yolo.csv', 'w', newline='') as csvfile:
                 writer = csv.writer(csvfile)
                 for line in output.decode().splitlines():
                    print(line)
                    if line.startswith("Duck Count=>"):
                        line_result = line.split('Duck Count=>')[1].strip()
                        duck_result = line_result.rstrip(',').split(",")
                        #Save to CSV incase
                        writer.writerow([duck_result])
                        #Save number of ducks to their classes
                        for duck_count in duck_result:
                            duck_strip = duck_count.strip()
                            result_split = duck_strip.split("=")
                            duck_class = result_split[0]
                            duck_num = result_split[1]
                            count_dict[duck_class].append(duck_num)

                    if line.startswith("totalFrame"):
                       self.index = int(line.replace("totalFrame",""))
                       
            # Calculate Average Number per Duck Class
            overall_total = 0
            for breed in count_dict:
                class_total = 0
                if count_dict:
                   for inx, i in enumerate(count_dict[breed]):
                       class_total = class_total + int(count_dict[breed][inx])

                   average_count = class_total / (self.index + 1)
                   overall_total = overall_total + average_count
                   AverageCount_dict[breed].append(average_count) 

            print(overall_total)
            AverageCount_dict["Total Count"].append(overall_total)  
             
            print(AverageCount_dict)
            process.kill()
            return AverageCount_dict

        #Upload file Function
        def UploadFile(self, load_anim, conf_thresh, modl_op):
            #File types
            FILE_TYPES_img = ['bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp', 'mpo']
            FILE_TYPES_vid = ['mov', 'avi', 'mp4', 'mpg', 'mpeg', 'm4v', 'wmv', 'mkv']
            self.file_upload = st.sidebar.file_uploader("Upload Video/Images", type=FILE_TYPES_img + FILE_TYPES_vid)
            if st.sidebar.button("Upload"):
                st.cache_resource.clear()
                self.file_type = self.file_upload.name.split(".")[1]
                self.uploadfile_name = self.file_upload.name.split(".")[0]
                print(self.uploadfile_name)
                  
                if self.file_type in FILE_TYPES_img:
                    self.tffile = tempfile.NamedTemporaryFile(suffix=f".{self.file_type}", delete=False)

                if self.file_type not in FILE_TYPES_img:
                    self.tffile = tempfile.NamedTemporaryFile(suffix=f".mp4", delete=False)
                    
                if self.file_upload:
                    self.tffile.write(self.file_upload.read())
                    dem_vid = open(self.tffile.name, "rb")
                    self.demo_bytes = dem_vid.read()
                    
                    #display uploaded file in sidebar
                    if self.file_type in ["mp4", "mov", "avi"]:
                            st.sidebar.text("Input Video")
                            st.sidebar.video(self.demo_bytes)

                    if self.file_type in ["png", "jpg", "jpeg"]:
                            st.sidebar.text("Input Image")
                            st.sidebar.image(self.demo_bytes)
                    st.empty()        

                    #processing detection
                    lottie_placeholder = st.empty()
                    self.load_anim = load_animurl(load_anim)
                    with lottie_placeholder:
                        st_lottie(self.load_anim, height=500, key="duck") 
                    
                    if modl_op == "YOLOv7":
                       self.output = DetectYolo(self, self.tffile.name, conf_thresh)
                    
                    # name of the file process
                    detect_name = os.path.basename(self.tffile.name)

                    #Ouput Section      
                    #image output
                    if self.file_type in FILE_TYPES_img:
                        #image path and streamlit output
                        detect_path = open(f"done_detect/{detect_name}", "rb")
                        self.detect_bytes = detect_path.read()
                        st.image(self.detect_bytes, use_column_width="auto")
                    
                    if self.file_type not in FILE_TYPES_img:
                        #convert process video to mp4 format
                        my_clip = VideoFileClip(f"done_detect/{detect_name}")
                        my_clip.write_videofile(f"done_detect/{self.uploadfile_name}.mp4")
                        #video path and streamlit output
                        detect_path_vid = open(f"done_detect/{self.uploadfile_name}.mp4", "rb")
                        os.remove(f"done_detect/{detect_name}")
                        self.detect_bytes = detect_path_vid.read()
                        st.video(self.detect_bytes)

                    lottie_placeholder.empty()

                    st.markdown("------")

                    st.markdown("""
                                    <div style="display: flex; align-items: center;">
                                        <h1 class="DCA">Ducks Count Average</h1>
                                    </div>
                                """, unsafe_allow_html=True)
                    
                    duck_class = []
                    str_cols = []
                    met_cols = []

                    for result_AV in self.output:
                        #print(self.output[result_AV])
                        if float(self.output[result_AV][0]):
                            duck_class.append(result_AV)
                                
                    for num in range(len(duck_class)):
                        str_cols.append(f"col{num}")

                    for metc in met_cols:
                        met_cols.append(eval(metc))

                    with st.container():
                        colindex = 0
                        met_cols  = st.columns(3 if len(duck_class) >= 3 else len(duck_class))
                        for result_AV in self.output:
                        #print(self.output[result_AV])
                            if float(self.output[result_AV][0]):
                                print(f"The Average Count of {result_AV} ====== {self.output[result_AV]}") 
                                round_num =  round(float(self.output[result_AV][0]), 2)
                                met_cols[colindex].metric(label=result_AV, value=round_num)
                                colindex = colindex + 1
                                if colindex == 3:
                                    colindex = 0

        

        #Real time Capture Function
        def RealTime(self):
            webrtc_streamer(key="sample")

        #Web App Title
        st.set_page_config(page_title="Duck Counting", page_icon=":bird:", layout="wide")
        st.title("Duck Counting")
       
        #side bar configuration
        st.sidebar.title("Configuration")
        st.sidebar.markdown("---")
        with open("dashboard.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True,)

        
        self.modl_opt = st.sidebar.selectbox("Select a Model to Run",("YOLOv7", "Coming soon", "Coming soon"))
                               
                               
        st.sidebar.markdown("----")
        st.markdown(
                """
                <style>
                [data-testid="stSidebar"][arial-expanded="true"] > div:first-child{width: 400px;}
                [data-testid="stSidebar"][arial-expanded="false"] > div:first-child{width: 400px; margin-left: -400px}
                </style>
                """,

                unsafe_allow_html=True,
                )
        
        
        #confidece threshold
        self.conf_thresh = st.sidebar.slider("Confidence", min_value=0.0, max_value=1.0, value=0.25)
        st.sidebar.markdown("----")
        
        #Select Detection Format
        self.file_format = st.sidebar.radio(
                            "Select Detection Format",
                            key="visibility",
                            options=["Real-Time Capture", "Upload File"],
                            )
        st.sidebar.markdown("----")
        
        if self.file_format == "Real-Time Capture":
           RealTime(self)     

        if self.file_format == "Upload File":    
            UploadFile(self, load_anim, self.conf_thresh, self.modl_opt)    
                    
 
                          
                            

                        
                                                  
                    
                                  
           
      

load_anim = "https://assets4.lottiefiles.com/packages/lf20_jxdtgpuk.json"

if __name__ == "__main__":
    try:
        DuckCounting(load_anim)
    except SystemExit:
        pass
            



