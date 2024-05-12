This telegram bot is designed to survey users, with the ability to select a topic.
It includes protection of questions from copying, deletion of answers and questions immediately after answering the question.
In a separate message there is a countdown. It is possible to send replies to several admins via telegram and specify an email for mailing.

For start bot:

```pip install -r requirements.txt```

Take your telegram token form Bot Father and add to environment or make config.py file.
Change email to yours in consts.py for mailing and add password the same way like telegram token.

Add topics to topics.json and make "questions" directory where will the text files with questions be stored.
File example:
1. How do you define system requirements based
   on the most successful ways in your experience?
   What methods and tools do you use for this? 2 min
2. ... 1 min 30 sec

Add "emails" directory with emails.txt where mailы will be stored for distribution.
For add admnins to send questions enter command: /admin
