import streamlit as st
import sys
import youtube_data
from youtube_data import *
import streamlit_nested_layout
import pandas as pd


#st.session_state.get_channel_btn_clicked = False
#if 'get_channel_btn_clicked' not in st.session_state:
#    st.session_state.get_channel_btn_clicked = False


# Create DB and Table is not exist
create_database()
create_database_and_table()


# session state to maintain entered channel id
if 'yt_channel_id' not in st.session_state:
    st.session_state.yt_channel_id = None

# session state to maintain channel data
if 'yt_channel_data' not in st.session_state:
    st.session_state.yt_channel_data = None

# session state to maintain playlist data
if 'yt_playlist_data' not in st.session_state:
    st.session_state.yt_playlist_data = None

def fetch_channel_data_all():
        if(channel_id):
            with st.spinner(text='Fetching channel info...'):
                    channelData = get_channel_data(channel_id= channel_id)
                    playlist_details = get_playlists_details(channel_id=channel_id)
                    st.session_state.yt_channel_data = channelData
                    st.session_state.yt_playlist_data = playlist_details
                    
                    st.toast("Channel info fetched successfully")
        else:
            st.warning(body="Please enter Channel Id...")



tab1, tab2 = st.tabs(["Search", "Query"])

with tab1:
    st.title('youtube harvesting')

        
    

    with st.form(key="form1", border= True, clear_on_submit=True):
        channel_id = st.text_input('Enter a channel id:', value= "")
        if(channel_id):
            st.session_state.yt_channel_id = channel_id

        submited = st.form_submit_button("Submit")
        if(submited):
            try:
                fetch_channel_data_all()

            except Exception as error:
                st.warning("Channel data not found.")
                st.write("Channel data not found." , error)




    channelPlaceHolder = st.empty()


    # display channel data
    if(st.session_state.yt_channel_data is not None):
        try:
            save_channel_data(st.session_state.yt_channel_data)
            with channelPlaceHolder.container(border=True):
                col1, col2 = st.columns([4,1])
                with col1:
                    st.write("<h4><u>Channel Information</u></h4>", unsafe_allow_html=True)
                with col2:
                    if st.button("Close", key= "channel_reset", type= "primary"):
                        st.session_state.yt_channel_data = None
                #st.write("---") # divider

                # show buttons in single row
                col1, col2 = st.columns([2,4])
                with col1:
                    st.write("**Channel Id:**")
                with col2:
                    st.write(channel_id)

                # show buttons in single row
                col1, col2 = st.columns([2,4])
                with col1:
                    st.write("**Channel Name:**")
                with col2:
                    st.write(st.session_state.yt_channel_data["channel_name"])

                # show buttons in single row
                col1, col2 = st.columns([2,4])
                with col1:
                    st.write("**Channel Description:**")
                with col2:
                    st.write(st.session_state.yt_channel_data["channel_desc"])

                # show buttons in single row
                col1, col2 = st.columns([2,4])
                with col1:
                    st.write("**Published at:**")
                with col2:
                    st.write(st.session_state.yt_channel_data["channel_pAt"])

                
                # show buttons in single row
                col1, col2 = st.columns([2,4])
                with col1:
                    st.write("**Video Count:**")
                with col2:
                    st.write(st.session_state.yt_channel_data["channel_videoC"])
                
                # show buttons in single row
                col1, col2 = st.columns([2,4])
                with col1:
                    st.write("**Subscriber Count:**")
                with col2:
                    st.write(st.session_state.yt_channel_data["channel_sub"])

                
                # display playlist data
                if(st.session_state.yt_playlist_data is not None):
                    # Save DB start
                    save_playlist_into_database(st.session_state.yt_playlist_data)
                    for ply_list in st.session_state.yt_playlist_data:
                        save_video_list_in_batabase(ply_list["video_data"])
                        for vid_list in ply_list["video_data"]:
                            save_comments_in_database(vid_list["comments"])
                    # Save DB start
                    try:
                        col1, col2 = st.columns([2,4])
                        with col1:
                            st.write("**Playlist:**")
                        with col2:
                            # selector for playlist
                            plist = st.selectbox(label= "Select Playlist", options= st.session_state.yt_playlist_data, format_func= lambda x: x["title"], label_visibility= "collapsed", placeholder="Select Playlist", index=0)
                        

                        if(plist):
                            # show buttons in single row
                            col1, col2 = st.columns([2,4])
                            with col1:
                                st.write("**Playlist Id:**")
                            with col2:
                                st.write(plist["playlist_Id"])

                            # show buttons in single row
                            col1, col2 = st.columns([2,4])
                            with col1:
                                st.write("**Title:**")
                            with col2:
                                st.write(plist["title"])

                            col1, col2 = st.columns([2,4])
                            with col1:
                                st.write("**Video List:**")
                            with col2:
                                # selector for video
                                video = st.selectbox(label= "Select Video", options= plist["video_data"], format_func= lambda x: x["Title"], label_visibility= "collapsed", placeholder="Select Playlist", index=0)
                        
                            if(video):
                                col1, col2 = st.columns([2,4])
                                with col1:
                                    st.write("**Video Id:**")
                                with col2:
                                    st.write(video["Video_Id"])

                                col1, col2 = st.columns([2,4])
                                with col1:
                                    st.write("**Video Title:**")
                                with col2:
                                    st.write(video["Title"])

                                col1, col2 = st.columns([2,4])
                                with col1:
                                    st.write("**Video Description:**")
                                with col2:
                                    st.write(video["Description"])

                                col1, col2 = st.columns([2,4])
                                with col1:
                                    st.write("**Total Views:**")
                                with col2:
                                    st.write(video["Views"])
                                
                                col1, col2 = st.columns([2,4])
                                with col1:
                                    st.write("**Total Likes:**")
                                with col2:
                                    st.write(video["Favourite_Count"])

                                col1, col2 = st.columns([2,4])
                                with col1:
                                    st.write("**Comments:**")
                                with col2:
                                    if(video["comments"]):
                                        for comment in video["comments"]:
                                            st.write("**Date:**", comment["Comment_published"])
                                            st.write("**Comment:**", comment["Comment_Text"])
                                            st.write(" ")

                                        


                    except Exception as error:
                        print("playlist Exception : ", error)

                else:
                    print("playlist null")

        except:
            channelPlaceHolder.empty()

    else:
        channelPlaceHolder.empty()


with tab2:
    st.title("Select Query")
    
    options = ["Select Query", 
                "What are the names of all the videos and their corresponding channels?", #1
                "Which channels have the most number of videos, and how many videos do they have?", #2
                "What are the top 10 most viewed videos and their respective channels?", #3
                "How many comments were made on each video, and what are their corresponding video names?", #4
                "Which videos have the highest number of likes, and what are their corresponding channel names?", #5
                "What is the total number of likes and dislikes for each video, and what are their corresponding video names?",#6
                "What is the total number of views for each channel, and what are their corresponding channel names?", #7
                "What are the names of all the channels that have published videos in the year 2022?", #8
                "What is the average duration of all videos in each channel, and what are their corresponding channel names?",#9
                "Which videos have the highest number of comments, and what are their corresponding channel names?"] #10
    query = st.selectbox(label= "Select Query", options= options, label_visibility= "visible", placeholder="Select Playlist", index=0)

    if(query):
        index = options.index(query)
        if index != 0:
            st.write("**Result**")
            result = None
            if(index == 1): #What are the names of all the videos and their corresponding channels?
                query = "SELECT title, channel_name FROM video;"
                result = execue_query(query)
            elif(index == 2): #Which channels have the most number of videos, and how many videos do they have?
                query = "SELECT channel_name, channel_videoC FROM youtube_data.channel WHERE channel_videoC = (SELECT MAX(channel_videoC) from youtube_data.channel);"
                result = execue_query(query)
            elif(index == 3): #What are the top 10 most viewed videos and their respective channels?
                query = "SELECT channel_name, title, views FROM youtube_data.video ORDER BY CAST(views AS unsigned) DESC LIMIT 10;"
                result = execue_query(query)
            elif(index == 4): #How many comments were made on each video, and what are their corresponding video names?
                query = "SELECT title, comments FROM youtube_data.video;"
                result = execue_query(query)
            elif(index == 5): #Which videos have the highest number of likes, and what are their corresponding channel names?
                query = "SELECT channel_name, like_count FROM youtube_data.video ORDER BY CAST(like_count AS unsigned) DESC LIMIT 10;"
                result = execue_query(query)
            elif(index == 6): #What is the total number of likes and dislikes for each video, and what are their corresponding video names?
                query = "SELECT title, like_count, dislike_count FROM youtube_data.video;"
                result = execue_query(query)
            elif(index == 7): #What is the total number of views for each channel, and what are their corresponding channel names?
                query = "SELECT channel_name, viewCount FROM youtube_data.channel;"
                result = execue_query(query)
            elif(index == 8): # What are the names of all the channels that have published videos in the year 2022?"
                query = "SELECT DISTINCT channel_name FROM video WHERE published_date LIKE '2022-%';"
                result = execue_query(query)
            elif(index == 9): #What is the average duration of all videos in each channel, and what are their corresponding channel names?
                query = """SELECT channel_name, AVG(duration) AS avg_duration_seconds FROM youtube_data.video GROUP BY channel_name;"""
                result = execue_query(query)
            elif (index == 10): #Which videos have the highest number of comments, and what are their corresponding channel names?
                query = """SELECT video.title as "Video title", COUNT(youtube_data.comment.comment_id) AS "comment_count" FROM youtube_data.video LEFT JOIN youtube_data.comment ON youtube_data.video.video_id = youtube_data.comment.video_id GROUP BY youtube_data.video.video_id, youtube_data.video.title ORDER BY comment_count DESC;"""
                result = execue_query(query)

            try:    
                pd.DataFrame(result)
                st.write(result)
            except Exception as error:
                print("Query Error:", error)


    



st.markdown(
    """
    <style>
    button[kind="primary"] {
        background: none!important;
        border: none;
        padding: 0!important;
        color: black !important;
        text-decoration: none;
        cursor: pointer;
        border: none !important;
    }
    button[kind="primary"]:hover {
        text-decoration: none;
        color: black !important;
    }
    button[kind="primary"]:focus {
        outline: none !important;
        box-shadow: none !important;
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

