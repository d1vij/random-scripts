#TODO: Look into encoding

# datetime in day-mnth-year 24hr:min:sec

import os 
import json
from datetime import datetime
import sqlite3

DATABASE = 'messages.db'
DIR="sw"

def list_of_json_files_in_dir(_dir) -> list[str]: 
    return [os.path.join(DIR,file) for file in os.listdir(_dir) if file.endswith('.json')]
def save_to_json(content):
    with open('parsed_messages.json','w',encoding='utf-8') as file:
        json.dump(content,file , ensure_ascii=False,indent=2)

def decode(s):
    return s.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')

def convert_timestamp_to_datestring(data):
    for _m in data["messages"]:
        timestamp_s = int(_m["timestamp_ms"])/1000
        dt = datetime.fromtimestamp(timestamp_s)
        _m['datetime'] = dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return data


def parse(files:list) -> dict[str,list[dict]]:
    all_documents = []
    participants = []

    for filename in files:
        with open(filename,'r',encoding='utf-8') as file:
            # length of all content should be the number of documents parsed
            document = json.loads(file.read())
            for entry in document['participants']:
                if entry['name'] not in participants:
                    participants.append(entry["name"])
            all_documents.append(document)

    print("Documents parsed = ", len(all_documents))
    print("Chat participants = ", *participants)
    
    
    # array of all the messages from all the documents
    messages = []
    for single_document in all_documents:
        for _m in single_document['messages']:
           messages.append(_m)
    print("Total messages found = ", len(messages))
    
    #cleaning up messages
    for _m in messages:
        keys = _m.keys()
        _m["type"] = None
        _m['content'] = _m.get("content")
        if "is_geoblocked_for_viewer" in keys:
            del _m["is_geoblocked_for_viewer"]
        if "is_unsent_image_by_messenger_kid_parent" in keys:
            del _m["is_unsent_image_by_messenger_kid_parent"]
        
        if "share" in keys :
            if "link" in _m["share"].keys():
                _m['type'] = "shared_reel"
                _m['content'] = _m['share']['link'] # replacing the content with the reel's link and removing everything

            else: #some other shared content
                _m["type"] = "shared_content"
                _m['content'] = _m['share'].get(list(_m.keys())[0], None)
                
                
            del _m['share']
            if "reactions" in keys:
                del _m['reactions']
            
        elif "content" in keys and "shared" not in keys:
            _m['type'] = "text"
            if "reactions" in keys:
                del _m['reactions']

        elif "photos" in keys:
            _m['type'] = "photo"
            _m['content'] = _m['photos'][0]['uri']

            del _m['photos']
            if "reactions" in keys:
                del _m['reactions']

        elif "videos" in keys:
            _m['type'] = "video"
            _m['content'] = _m['videos'][0]['uri']
        
            del _m['videos']
            if "reactions" in keys:
                del _m['reactions']


        
    return {
        "participants":participants,
        "messages":messages
    }        




def save_to_sqlite(data:list[dict]) -> None:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("drop table if exists messages;")
    conn.commit()
    cursor.execute("""create table messages(type varchar(10),
                                            sender varchar(64),
                                            content text,
                                            datetime datetime);""")
    conn.commit()
    
    data_to_store = []
    for _m in data:
        data_to_store.append((_m["type"], _m["sender_name"], _m["content"], _m["datetime"]))
        # print(_m)

    cursor.executemany("insert into messages(type, sender, content, datetime) values(?, ?, ?, ?);",data_to_store)
    conn.commit()
    
    cursor.close()
    conn.close()



def main():
    files = list_of_json_files_in_dir(DIR) 

    _parsed_content:dict = convert_timestamp_to_datestring(parse(files))
    # save_to_json(_parsed_content)
    # print('saved to json')

    save_to_sqlite(_parsed_content["messages"])
    print('saved to sqlite')

    
    
if __name__ == "__main__":
    main()