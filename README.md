# Mutual-Fund-Updater
A simple app that texts NAV updates to user's cell phones for selected mutual funds on a chosen schedule.

# Objectives
Initially this was just going to be something to build out for another application I had in mind. I may use this as an API for that project in the future but I think I'll leave this as a standalone project for now. While my Vanguard brokerage will email me price updates for funds on my watchlist I kind of like having a quick text on a particular Fund I'm holding once in awhile without having to wade through all the noise.
I mainly wanted to practice my Python skills to build something moderately useful with RESTful architecture.

# Obstacles
- Finding an api that was easy to use, solid, and not deprecated. 
  + Google Finance worked for a bit.
  + Currently using Yahoo-Finance with some try except hack workarounds.
  + Still looking.
- Scheduling:
  + Initially used threading.Thread module but found getting threads to stop a huge pain. Killing threads isn't even strictly       allowed thanks to the Global Interpreter Lock and while I understand why this is best practice it was very frustrating.
  + Multiprocessing library worked fairly well when it came time to getting updates to stop but I ultimately went with the         APScheduler. Which was perfect for my simple scheduling needs until . . .
- Deployment:
  + I already used Heroku for a Java app so I thought I'd try something easy . . 
  + After getting my app up and running on PythonAnywhere I noticed I couldn't get the updates to stop even when the funds and     pid's were removed from the database. PythonAnywhere does not support APScheduler. 
  + Which led me to AWS. Upon watching a tutorial from Andrew T. Baker (https://www.youtube.com/watch?v=vGphzPLemZE) on             five ways to deploy a Flask app I decided to use Zappa and AWS Lambda. It's an easy deploy for "Hello Cruel World" but         after a sourjorn with setting up a Redis db and experimenting with Celery I realized that AWS doesn't support Python 3.5.       Really? 2.7 or 3.6 only
  + to be continued
 
 # Some Lessons Learned
 - If managing and messaging all the different libraries, systems, and versions thereof in order to hack something into working    live is Dev Ops I'm not sure that's how I'd like to spend my career. 
 - Orthoganality is a bitch.
 - Without a client, the software is never "done".
 
 # Results
 - The fund updater functions well, locally.
 - Currently running on PythonAnywhere is the equivalent of dynamic screen shots.
 
