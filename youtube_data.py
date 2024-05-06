import googleapiclient.discovery
from datetime import datetime
import mysql.connector
import pandas as pd

api_service_name = "youtube"
api_version = "v3"
api_key="AIzaSyAiKKhDUbiCzFfCejac-MMoSJ5Mb9Df0z8"

# create youtube context
youtube = googleapiclient.discovery.build(
api_service_name, api_version, developerKey=api_key)


def create_database():
    try:   
        db_client = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "4444")
        cursor = db_client.cursor()
        
        # TO CREATE A DATABASE    
        query = "CREATE DATABASE IF NOT EXISTS youtube_data"      
        cursor.execute(query)
    except Exception as error:
        print("Create DB error ", error)



# Sql Client with exist DB
def getSqlClient():
    client = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "4444",
        database = "youtube_data"
    )
    return client

def convert_timstamp_to_date(original):
    # Parse the timestamp string
    try:
        timestamp_obj = datetime.strptime(original, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError as valueError:
        timestamp_obj = datetime.strptime(original, '%Y-%m-%dT%H:%M:%SZ')

    # Format the timestamp in the required format
    formatted_timestamp = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_timestamp




# create tables
def create_database_and_table():
    client = getSqlClient()
    cursor = client.cursor()
    
    # Create "Channel" TABLE 
    query = """create table IF NOT EXISTS Channel(channel_id varchar(255) PRIMARY KEY,channel_name varchar(255) ,channel_description text,channel_publishedAt timestamp,playlists_id varchar(255),channel_sub int,channel_videoC int,viewCount varchar(255), thumbnail_url varchar(256))"""
    cursor.execute(query)

    # Create "playlist" table
    query ="""create table IF NOT EXISTS playlist(playlist_id varchar(255) PRIMARY KEY,title varchar(255), channel_id varchar(255),channel_name varchar(255),playlist_name varchar(255),publishedAt datetime,video_count int)"""
    cursor.execute(query)

    # Create "video" table
    query = """create table IF NOT EXISTS video(channel_name varchar(225),channel_id varchar(255),video_id varchar(255) PRIMARY KEY,title varchar(255),tags varchar(255),thumbnail varchar(255),description text, published_date datetime, duration varchar(255),views varchar(255),comments varchar(255),favourite_count varchar(255),definition varchar(255),caption_status varchar(255), like_count varchar(255), dislike_count varchar(255))"""
    cursor.execute(query)

    # Create "comment" table
    query = """create table IF NOT EXISTS comment(comment_id varchar(255) PRIMARY KEY,video_id varchar(255),comment_text text,comment_author varchar(255),comment_publishedAt datetime)"""
    cursor.execute(query)

    client.close()


# Get channel info from Youtube
def get_channel_data(channel_id):
    request = youtube.channels().list(
        part="snippet,content Details,statistics",
        id=channel_id
    )
    response = request.execute()
    print(response)
    data = {
        "channel_Id":channel_id,
        "channel_name":response['items'][0]['snippet']['title'],
        "channel_desc":response['items'][0]['snippet']['description'],
        "channel_pAt":response['items'][0]['snippet']['publishedAt'],
        "channel__pId":response['items'][0]['contentDetails']['relatedPlaylists']['uploads'],
        "channel_sub":response['items'][0]['statistics']['subscriberCount'],
        "channel_videoC":response['items'][0]['statistics']['videoCount'],
        "channel_views":response['items'][0]['statistics']['viewCount'],
        "thumbnail_url":response['items'][0]['snippet']['thumbnails']['default']['url']
    }
    return data

# Store channel data in mySQL
def save_channel_data(channel_details):
    try:
        client = getSqlClient()
        cursor = client.cursor()
        query = """INSERT INTO channel(channel_id,channel_name,channel_description,channel_publishedAt,playlists_id,channel_sub,channel_videoC,viewCount, thumbnail_url) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        print(query)

        # Parse the timestamp string
        # Format the timestamp in the required format
        formatted_timestamp = convert_timstamp_to_date(channel_details["channel_pAt"])


        values =(channel_details["channel_Id"],
            channel_details["channel_name"],
            channel_details["channel_desc"],
            formatted_timestamp,
            channel_details["channel__pId"],
            channel_details["channel_sub"],
            channel_details["channel_videoC"],
            channel_details["channel_views"],
            channel_details["thumbnail_url"]
        )
        print(values)
        cursor.execute(query, values)
        client.commit()
        client.close()
    except Exception as error:
         print('Channel insertion error=>', error)


# fetch playlist by channel id
def get_playlists_details(channel_id):
    playlists_details = []
    next_page_token = None
    while True:
        request = youtube.playlists().list(
            part = "snippet,contentDetails,id,status",
            channelId = channel_id,
            maxResults = 50,
            pageToken = next_page_token
        )
        response = request.execute()

        print("Playlist response: ",response)

        for item in response['items']:
            video_ids = get_video_ids(playlist_Id=item['id'])
            comments = get_comment_info(video_ids=video_ids)
            data = dict(playlist_Id = item['id'],
                        title = item['snippet']['title'],
                        channel_Id = item['snippet']['channelId'],
                        channel_Name = item['snippet'][ 'channelTitle'],
                        publishedAt = item['snippet']['publishedAt'],
                        Video_Count = item['contentDetails']['itemCount'],
                        video_ids = video_ids,
                        video_data = get_video_details(video_ids= video_ids),
                        comments = comments

            )
            playlists_details.append(data)
       
        next_page_token = response.get(next_page_token)
        if next_page_token is None:
            break
   
    return playlists_details

# save playlist data into DB
def save_playlist_into_database(playlists_detail):
    try:
        client = getSqlClient()
        cursor=client.cursor()
        for plist in playlists_detail:
            query = """insert into playlist(playlist_Id,title,channel_Id,channel_name,publishedAt,video_Count) values(%s,%s,%s,%s,%s,%s)"""
            print(playlists_detail)

            timestamp_obj = datetime.strptime(plist["publishedAt"], '%Y-%m-%dT%H:%M:%SZ')
            formatted_timestamp = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')



            values =(plist["playlist_Id"],
                    plist["title"],
                    plist["channel_Id"],
                    plist["channel_Name"],
                    formatted_timestamp,
                    plist["Video_Count"]
                    )
            cursor.execute(query, values)
            client.commit()
        client.close()
    except Exception as error:
        print("playlist insetion error=>", error)



# get video ids
def get_video_ids(playlist_Id):
    video_ids = []
    next_page_token = None

    while True:
        response1 = youtube.playlistItems().list(part = 'snippet',
                                                playlistId = playlist_Id,
                                                maxResults = 50,
                                                pageToken = next_page_token).execute()
        
        print("playlistItems :", response1)
 

        for i in range(len(response1['items'])):
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])

        next_page_token = response1.get('nextPageToken')
        
        if next_page_token is None:
            break
    return video_ids


def get_video_details(video_ids):
    video_data = []
    try:
        #for video_id in video_ids:
        request = youtube.videos().list(
            part = "snippet,contentDetails,statistics",
            id = video_ids
        )
        response = request.execute()

        for item in response['items']:    
            print("Video:", item)                                        
            
            data = dict(Channel_Name = item ['snippet']['channelTitle'],
                        Channel_Id = item ['snippet'][ 'channelId'],
                        Video_Id = item ['id'],
                        Title = item ['snippet']['title'],
                        Tags = item.get('tags'),                                   # SOME VIDEOS DONT HAVE THIS VALUE,SO TO AVOID GETTING ERROR WE USE .GET FUNCTION
                        Thumbnail = item ['snippet']['thumbnails']['default']['url'],
                        Description = item.get('description'),
                        Published_Date = item ['snippet']['publishedAt'],
                        Duration = iso8601_to_seconds(item ['contentDetails']['duration']),
                        Views = item ['statistics']['viewCount'],
                        Comments = item ['statistics']['commentCount'],
                        Favourite_Count = item ['statistics']['favoriteCount'],
                        Like_Count = item ['statistics']['likeCount'],
                        Dislike_Count = '0',
                        Definition = item ['contentDetails']['definition'],
                        Caption_Status = item ['contentDetails']['caption'],
                        comments = get_comment_data(video_id=item['id'])
                        )
            video_data.append(data)
    except Exception as error:
        print("get_video_details Error=>", error)

    return video_data

# Get Comment details by video IDs
def get_comment_info(video_ids):
    comment_data = []
    try:
        for video_id in video_ids:
            print("get_comment_info video_id : ", video_id)
            request = youtube.commentThreads().list(
                part = "snippet",
                videoId = video_id,                
                maxResults = 50)
            response = request.execute()

            for item in response['items']:
                data = dict(Comment_Id = item['snippet']['topLevelComment']['id'],
                            video_Id = item['snippet']['topLevelComment']['snippet']['videoId'],                            
                            Comment_Text = item['snippet']['topLevelComment']['snippet']['textDisplay'],
                            Comment_Author = item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            Comment_published = item['snippet']['topLevelComment']['snippet']['publishedAt']
                            )
                comment_data.append(data)
    except Exception as error:
        print("get_comment_info error=>", error)
      
    return comment_data

# Get Comment details by video IDs
def get_comment_data(video_id):
    comment_data = []
    try:
        request = youtube.commentThreads().list(
            part = "snippet",
            videoId = video_id,                
            maxResults = 50)
        response = request.execute()

        for item in response['items']:
            data = dict(Comment_Id = item['snippet']['topLevelComment']['id'],
                        video_Id = item['snippet']['topLevelComment']['snippet']['videoId'],                            
                        Comment_Text = item['snippet']['topLevelComment']['snippet']['textDisplay'],
                        Comment_Author = item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        Comment_published = item['snippet']['topLevelComment']['snippet']['publishedAt']
                        )
            comment_data.append(data)
    except Exception as error:
        print("get_comment_info error=>", error)
      
    return comment_data

# Save Video in database
def save_video_list_in_database(video_list):
    try:
        client = getSqlClient()
        cursor=client.cursor()
        for video in video_list:
            query = """insert into video(channel_name,channel_id,video_id,title,tags,thumbnail,description, published_date, duration,views,comments,favourite_count,definition,caption_status, like_count, dislike_count) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            print("Video : ", video)

            timestamp_obj = datetime.strptime(video["Published_Date"], '%Y-%m-%dT%H:%M:%SZ')
            formatted_timestamp = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
            print("formatted_timestamp : " , formatted_timestamp)

            values =(video["Channel_Name"],
                    video["Channel_Id"],
                    video["Video_Id"],
                    video["Title"],
                    video["Tags"],
                    video["Thumbnail"],
                    video["Description"],
                    formatted_timestamp,
                    video["Duration"],
                    video["Views"],
                    video["Comments"],
                    video["Favourite_Count"],
                    video["Definition"],
                    video["Caption_Status"],
                    video["Like_Count"],
                    video["Dislike_Count"]
                    )
            print(values)
            cursor.execute(query, values)
            client.commit()
        client.close()
    except Exception as error:
        print("video insetion error=>", error)

# Save Comments in database
def save_comments_in_database(comment_list):
    try:
        client = getSqlClient()
        cursor=client.cursor()
        for comment in comment_list:
            query = """insert into comment(comment_id,video_id,comment_text,comment_author,comment_publishedAt) values(%s,%s,%s,%s,%s)"""

            timestamp_obj = datetime.strptime(comment["Comment_published"], '%Y-%m-%dT%H:%M:%SZ')
            formatted_timestamp = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')



            values =(comment["Comment_Id"],
                    comment["video_Id"],
                    comment["Comment_Text"],
                    comment["Comment_Author"],
                    formatted_timestamp)
            
            print(values)
            cursor.execute(query, values)
            client.commit()
        client.close()
    except Exception as error:
        print("comments insetion error=>", error)


# Execute Query
def execue_query(query):
    try:
        client = getSqlClient()
        df = pd.read_sql_query(query, client)

        
        client.close()
        return df
    except Exception as error:
        print("Query error=>", error)


def iso8601_to_seconds(duration):
    try:
        sec = pd.Timedelta(duration).seconds

        print("iso8601_to_seconds duration : ", duration+" Seconds : ", sec)
        return sec
    except Exception as err:
        print("iso8601_to_seconds Error : ", err)
        return duration


