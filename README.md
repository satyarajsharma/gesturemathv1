Use main.py, open terminal in Pycharm to lauunch is using "streamlit run mainv.py"
=====================================

created with help from this video https://www.youtube.com/watch?v=RhhN0CLnFdc
uses cvzone and google gemini 2.5 free api. the APi stuff has changed drastically compared to last time.
uses streamlit to show output in browser. very pretty tbh. 

IMPORTANT - bring ur own API and don't expose it on github by leaving it in code and committing, or else it'll be tracked and deleted the next minute by google. 

1. main is just "Basic Hand Tracking Script".

2. v2 and v4 run in a browser window using Streamlit. you'll need to Open them in PyCharm terminal and write - "streamlit run mainv4.py" (if its mainv4.py or change it to mainv2.py in case of v2). it might ask for email, just press enter and then browser window will open. allow if it asks for permissions

hand tracking works as follows - if 1 fingers is visible, it will track the movement of that finger and draw stuff. if two fingers show up, it will stop tracking, this can be useful for drawing pauses. raising the thumb and 3 fingers at once (total 4, pinky is not included) will prompt a screenshot and the data will be sent to the gemini api

3. "mainv2" is a script with Gemini 2.5 Integration & API is via env-variable. "mainv4" is hardcoded API, perfect for testing. v3 is deleted.

4. "mainv3" is also has hardcoded API for testing, but the results show up in terminal, and webcam opens in a separate window for testing purposes.

5. "test camera" is just used to check which cameras work. might implement the camera naming here in future.


---------------
