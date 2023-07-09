# Pdf2Bot
This repository is a submission for **Google Cloud - VertexAI hackathon** conducted by lablab.ai. The repository contains the code and other data related to Pdf2Bot web-app. 


![bg](https://github.com/SrinadhVura/Pdf2Bot/assets/83588454/9d3c30e2-42d3-41ec-80d2-b32a598a1463)

## What is Pdf2Bot?
Pdf2Bot is a web-app that creates a chatbot on the fly from the document uploaded by the user and will be able to answer any kind of query related to the file. The thus built bot also outputs the answer in one of the seven widely accepted accents of English, world-wide.

## How to use Pdf2Bot?


## How to use Pdf2Bot locally?
1. Download the repository as a compressed directory, then extract it or using the *git clone* command.
2. Open the terminal.
3. Navigate to the directory where extracted repository is stored.
4. Run the following command to install required python libraries
   > pip install -r requirements.txt
5. Use the below command to run the app
   > streamlit run app.py

## Procedure
1. In the sidebar of the web-app click on upload, browse through the local file system and upload the file (As PDF)
2. After uploading the file click on *Done Uploading* button.
3. Wait until
   ```
   Uploaded
   Loaded
   Splitting done
   Vectorising done
   ```
   appears.
4. Enter the query. Click on *Submit* button
5. The answer as text and audio will be displayed by the app


## Technologies used
1. Python
2. Streamlit
3. Langchain
4. VertexAI
5. GTTS
6. Google Cloud

[Pdf 2 bot.pdf](https://github.com/SrinadhVura/Pdf2Bot/files/11995424/Pdf.2.bot.pdf)


   

