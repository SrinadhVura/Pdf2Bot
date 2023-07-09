#-----------------------------------------------------------------------------imports----------------------------------------------------------------------------------"""


import streamlit as st # we are using streamlit to create a web app
import tempfile # we are using tempfile to create a temporary directory to store the pdf file
import os # we are using os to join the path of the temporary directory and the pdf file
from PIL import Image # we are using PIL to add a background image to the web app
from google.auth import credentials # we are using google.auth to access google cloud service account
from google.oauth2 import service_account
import google.cloud.aiplatform as aiplatform
import vertexai # vertexai is a python library to access google cloud vertex ai
import json # we are using json to load the  json file
from gtts import gTTS # we are using gTTS to convert text to speech
from io import BytesIO # we are using BytesIO to convert the audio file to bytes
from pygame import mixer # we are using mixer to play the audio file
from langchain.embeddings import VertexAIEmbeddings # we are using VertexAIEmbeddings to create embeddings from the text
from langchain.vectorstores import Chroma # we are using Chroma to create a vector store from the embeddings
from langchain.chains import RetrievalQA # we are using RetrievalQA to create a chatbot from the vector store
from langchain.document_loaders import PyPDFLoader # we are using PyPDFLoader to load the pdf file
from langchain.agents.agent_toolkits import * 
from langchain.llms import VertexAI 
from pydantic import BaseModel # we are using BaseModel to create a custom class
from langchain.text_splitter import RecursiveCharacterTextSplitter # we are using RecursiveCharacterTextSplitter to split the text into chunks
import base64 # we are using base64 to encode the background image
import time # we are using time to record rate limit


#-----------------------------------------------------------------code to access google cloud service account----------------------------------------------------------------------------------"""


# Load the service account json file
# Update the values in the json file with your own
# Utility functions for Embeddings API with rate limiting
with open("service_account.json") as f:  # replace 'serviceAccount.json' with the path to your file if necessary
    service_account_info = json.load(f)
my_credentials = service_account.Credentials.from_service_account_info(service_account_info)
aiplatform.init(credentials=my_credentials)
# Initialize Google AI Platform with project details and credentials

with open("service_account.json", encoding="utf-8") as f:
    project_json = json.load(f)
    project_id = project_json["project_id"]
vertexai.init(project=project_id, location="us-central1")



#-----------------------------------------------------------------code of functions to initialize text bison model----------------------------------------------------------------------------------"""





def rate_limit(max_per_minute):
    period = 60 / max_per_minute
    print("Waiting")
    while True:
        before = time.time()
        yield
        after = time.time()
        elapsed = after - before
        sleep_time = max(0, period - elapsed)
        if sleep_time > 0:
            print(".", end="")
            time.sleep(sleep_time)


class CustomVertexAIEmbeddings(VertexAIEmbeddings, BaseModel):      # Custom class to override the embed_documents method
    requests_per_minute: int
    num_instances_per_batch: int

    # Overriding embed_documents method
    def embed_documents(self, texts):
        limiter = rate_limit(self.requests_per_minute)           # Rate limiting the API calls
        results = []
        docs = list(texts)

        while docs:
            # Working in batches because the API accepts maximum 5
            # documents per request to get embeddings
            head, docs = (
                docs[: self.num_instances_per_batch],
                docs[self.num_instances_per_batch :],
            )
            chunk = self.client.get_embeddings(head)
            results.extend(chunk)
            next(limiter)

        return [r.values for r in results]

# Initialize Vertex AI Embeddings with the Vertex AI client
llm = VertexAI(
    model_name="text-bison",
    max_output_tokens=1024,
    temperature=0.3,
    # top_p=0.8,
    # top_k=40,
    verbose=True,
)



#-----------------------------------------------------------------code of the web app design and working----------------------------------------------------------------------------------"""




embeddings = CustomVertexAIEmbeddings(llm=llm,requests_per_minute=1000,num_instances_per_batch=5)       # use embeddings from text bison to create chatbot from PDF provided by user
title = '<p style="font-family:Algerian; color:#004d00; font-weight:bold;  text-align:center;font-size: 60px;">&#128196 PDF2Bot &#129302</p>'
st.markdown(title, unsafe_allow_html=True)
description="<p style='font-family:cursive; color:#66ffff; font-weight:bold; text-align:center; font-size: 14px;'>This app uses google cloud text-bison model to create a chatbot from a PDF provided by the user. The chatbot is trained on the text from the PDF and can be used to answer questions about the PDF.</p>"
st.markdown(description, unsafe_allow_html=True)
def add_bg_from_local(image_file):              # function to add background image to the web app
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
add_bg_from_local('cover.png')              # add background image to the web app
footer="""<style>                            
a:link , a:visited{                                                                                         
color: blue;                                            
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: black;
color: white;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with ❤ by <a style='display: block; text-align: center;' href="https://github.com/SrinadhVura/VertexAI-hack" >Srinadh Vura <br> </a>Disclaimer: Please use smaller files for testing to avoid large delay (<100 pages) &#128517 &#128519</p>
</div>
"""


#-----------------------------------------------------------------code of the sidebar for uploading the PDF----------------------------------------------------------------------------------"""



st.sidebar.markdown(footer,unsafe_allow_html=True)
sbartitle='<p style="font-family:Algerian; color:Red; font-size: 24px;">Gimme the PDF to learn</p>'
st.sidebar.markdown(sbartitle, unsafe_allow_html=True)
upload=st.sidebar.file_uploader(":+1: Upload your PDF",type=['pdf'])
done=st.sidebar.button("Done uploading")
if done is not None:                # if the user clicks on done uploading, the pdf is uploaded to the web app
    while upload is None:               # wait for the user to upload the pdf
        time.sleep(10)
    tdir=tempfile.TemporaryDirectory()          # create a temporary directory to store the pdf
    tpath=os.path.join(tdir.name,'file.pdf')
    with open(tpath,'wb') as f:
        f.write(upload.getbuffer())
    x='<p style="font-family:Sans-serif; color:#ffe680; font-size: 18px;">Uploaded</p>'
    st.sidebar.markdown(x, unsafe_allow_html=True)
    data=PyPDFLoader(tpath)             # load the pdf
    docs=data.load()                                    
    x='<p style="font-family:Sans-serif; color:#ffe680; font-size: 18px;">Loaded</p>'
    st.sidebar.markdown(x, unsafe_allow_html=True)
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=0)                   # split the text into chunks of 1000 words
    docs=text_splitter.split_documents(docs)                                                        
    print(docs)
    x='<p style="font-family:Sans-serif; color:#ffe680; font-size: 18px;">Splitting done</p>'
    st.sidebar.markdown(x, unsafe_allow_html=True)
    database=Chroma.from_documents(docs,embeddings)
    print(database)
    x='<p style="font-family:Sans-serif; color:#ffe680; font-size: 18px;">Vectorizing done</p>'   
    st.sidebar.markdown(x, unsafe_allow_html=True)
    ret=database.as_retriever(search_type="similarity",search_kwargs={"k":1})                                   # create a retriever from the vector store
    qa=RetrievalQA.from_chain_type(llm=llm,chain_type="stuff",retriever=ret,return_source_documents=True)
    prompt=st.text_input("Input your query : ")                                                     # take the query from the user
    req_tld=st.selectbox("Choose an accent",["com.au","co.uk","us","ca","co.in","ie","co.za"])          # take the accent from the user
    st.write("* Australian English - com.au\n* British English - co.uk\n* American English - us\n* Canadian English - ca\n* Indian English - co.in\n* Irish English - ie\n* South African English - co.za")
    submit=st.button("Submit")
    while submit is None:                                                       # wait for the user to click on submit
        time.sleep(10)
    if submit is not None:                                                          # if the user clicks on submit, the query is answered               
        while prompt is None:
            time.sleep(10)
        if prompt is not None:                                                  # if the user enters a query, the query is answered
            prompt=prompt.strip()+" ? "                                
            res=qa({"query":prompt})                                        # pass the query to the chatbot
            print(res)                                                          # print the answer
            myobj = gTTS(text=res["result"],lang='en', slow=False, tld=req_tld) # convert the answer to speech
            mp3_fp = BytesIO()                                                                  # BytesIO object to store the audio file
            myobj.write_to_fp(mp3_fp)                                                   # convert the audio file to bytes
            st.audio(mp3_fp, format='audio/mp3')                                # play the audio file
            st.write("\n\n\n")
            st.write("The answer is : \n",  res["result"])                      # print the answer on the web app
