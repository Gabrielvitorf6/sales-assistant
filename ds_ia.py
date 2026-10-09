import pandas as pd
from google import genai
import os
import streamlit as st
import plotly.express as px
from streamlit import chat_message

st.set_page_config(page_title="Sales data anlysis using AI", layout="wide")

st.title("Sales data analysis using AI")

#AI client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) #We NEVER use a hardcoded AI, because we can get "hacked". Instead,
# we pass a variable inside .env file that will be set and will not be commited,exposed, etc.

if not os.getenv("GEMINI_API_KEY"): #Throwing error if there is no API key
    st.error("Please provide and Gemini API key to enable AI features")

#file upload
file = st.file_uploader("Upload your Excel sheet (.xlsx or .csv)" ,type=["xlsx","csv"]) #file uploader button and allowed file types

if file: #Checking if there is a file. Validated file format and read. Throw error if cannot read file
    if file.name.endswith(".xlsx"):
        df = pd.read_excel(file)
    elif file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        st.error("Cannot read file. Try it again")

    #Dataframe view
    st.subheader("Sales data sample")
    st.dataframe(df.head(10), use_container_width=True)

    #Statistic info
    st.subheader("Statistic information about the sales data")
    st.write(df.describe())

    #Detecting numerical and categorical columns. Helpful to create the bar plot after
    number_columns = df.select_dtypes(include=["number"]).columns.tolist()
    cat_columns = df.select_dtypes(exclude=["number"]).columns.tolist()

    #dinamic graph
    if number_columns and cat_columns: #Checking if there is at least one numerical and one categorical column in dataframe
        x = st.selectbox("Select a column to X axys", cat_columns) #select button to choose the X variable for graphic
        y = st.selectbox("Select a column to Y axys", number_columns) #select button to choose the y variable for graphic

        fig = px.bar(df, x=x,y=y, title=f"Graphic of {x} by {y}")#Creating barplot and formating a title string with the x and y columns
        st.plotly_chart(fig, use_container_width=True) #Show the graph on screen

#AI Assistant
    st.subheader("Make a question to AI")
    question = st.chat_input("EX: What is the average sales by category?") #Text input field

    # passing the question as a prompt to AI model
    if question: #if there is a question
        with st.chat_message("User"): #starting chat message component. The "user"  is to set the avatar in the chat
            st.write(question) #Showing the question in the chat

            #Passing the dataframe resume (first few lines) as string to AI read in the prompt
            resume = df.head(100).to_string()

            #The prompt to AI read and answer. The triple quotes is to wrap line if the text is too long, and the f is to format
            #variables as strings inside another strings
            prompt = f"""
                    You are a data Analyst.
                    
                    Analyze the sales table below and answer my question:
                    
                    Data:{resume}
                    
                    Question:{question}
                        """

            #Sending the prompt to our openai model
            answer = client.models.generate_content(
                       model="gemini-2.5-flash",
                    contents=prompt,
                    )

            #Returning the AI answer
            with chat_message("AI"):
                st.write(answer.text) #Convert the AI answer to text and show in the streamlit chat