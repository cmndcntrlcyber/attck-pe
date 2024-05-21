# ATTCK-PE (Portable Executor)
**Levaraging the power of the ATT&CK Database to enrich an AI agent to deployed as a browser thread for Adversary Emulation from a container**
### [ATT&CK Database](https://cmndcntrl.notion.site/ATT-CK-TTP-Database-82388bfa18a6411c8bdf844a7880bc6b)
- Initial Plan
    Create an [agent.](http://agent.py/)py file that does the following:
    
    1. receive the ATT&CK TTP prompt from the user
        
        ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/6a969394-6c77-4ae0-add7-cf2ff01004c6/4f75e153-e316-4cd0-9063-cfd9209bdebc/Untitled.png)
        
    2. searches its resources for the right URL
        1. uses Vector DB workers to send requests to the ATTCK Database 
        2. Identifies the correct ATTCK content to execute the request
    3. Offers the most aligned URL with the users’ prompt request
    4. Requests the raw byte-string data from the URL webpage
    5. AES256 decrypts the byte-string data 
    6. Executes the content of the decrypted byte-string data as a new thread
