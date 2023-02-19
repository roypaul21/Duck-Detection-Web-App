import streamlit as st
import cv2
import requests
from streamlit_lottie import st_lottie
import streamlit.components.v1 as components
from streamlit_webrtc import webrtc_streamer
import tempfile



class DuckCounting():

    def __init__(self, load_anim):
        st.set_page_config(page_title="Duck Counting", page_icon=":bird:", layout="wide")
        #Page
        st.title("Duck Counting")


        #side bar configuration
        st.sidebar.title("Configuration")
        st.sidebar.markdown("---")
        with open("dashboard.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True,)

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
        
        
        self.file_format = st.sidebar.radio(
                            "Select Detection Format",
                            key="visibility",
                            options=["Real-Time Capture", "Upload File"],
                            )
        st.sidebar.markdown("----")

        #open cam
        if self.file_format == "Real-Time Capture":
             webrtc_streamer(key="sample")
        
        #uploading file
        if self.file_format == "Upload File":
            self.file_upload = st.sidebar.file_uploader("Upload Video/Images", type=["mp4", "mov", "avi", "png", "jpg", "jpeg"])
            self.tffile = tempfile.NamedTemporaryFile(suffix=".mp4 .png", delete=False)
        
            if st.sidebar.button("Upload"):
                print(self.file_upload)
                if self.file_upload:
                    self.tffile.write(self.file_upload.read())
                    dem_vid = open(self.tffile.name, "rb")
                    demo_bytes = dem_vid.read()
    
                    st.sidebar.text("Input Video")
                    st.sidebar.video(demo_bytes)
                    
            st.sidebar.markdown("----")
                    
            
        

        

      
       
       
        '''
        # Load animation Gif
        def load_animurl(url):
            r = requests.get(url)
            if r.status_code != 200:
                return None
            else:
                return r.json()   
           
        self.load_anim = load_animurl(load_anim)
        st_lottie(self.load_anim, height=500, key="duck") 
        '''
      


        
          

load_anim = "https://assets8.lottiefiles.com/packages/lf20_ojxibjmr.json"

if __name__ == "__main__":
    try:
        DuckCounting(load_anim)
    except SystemExit:
        pass
            



