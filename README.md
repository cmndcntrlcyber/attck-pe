# ATTCK-PE (Portable Executor)
**Levaraging the power of the ATT&CK Database to enrich an AI agent to deployed as a browser thread for Adversary Emulation from a container**
### [ATT&CK Database](https://cmndcntrl.notion.site/ATT-CK-TTP-Database-82388bfa18a6411c8bdf844a7880bc6b)
- Initial Plan
    Create an [agent.](http://agent.py/)py file that does the following:
    ![console output](https://github.com/cmndcntrlcyber/attck-pe/assets/47669879/4e8b1d28-fc54-4c6c-a4e3-2013ce96dbae)

    1. receive the ATT&CK TTP prompt from the user
        
    2. searches its resources for the right URL
        1. uses Vector DB workers to send requests to the ATTCK Database 
        2. Identifies the correct ATTCK content to execute the request
    3. Offers the most aligned URL with the users’ prompt request
    4. Requests the raw byte-string data from the URL webpage
    5. AES256 decrypts the byte-string data 
    6. Executes the content of the decrypted byte-string data as a new thread

## Contributing
Contributions, suggestions, and feedback are welcome. Please create an issue or pull request for any contributions.

1. Fork the repository.
2. Create a new branch for your `username-dev` (e.g. `cmndcntrlcyber-dev`) feature (e.g. `cmndcntrlcyber-feat`) or bug fix (e.g. `cmndcntrlcyber-fix`).
3. Make your changes and commit them.
4. Push your changes to your forked repository.
5. Open a pull request in the main repository.
