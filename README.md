# Utd Rooms
Utility tool to find open locations at UTD, see links for professor ratings, and links for grade distribution of courses. 

### How are open locations determined? 
- I scraped all UTD coursebook (tool that shows information about class times, professor, and location). So, anytime there is no lecture happening then the class is probably open. "Probably" because some rooms might be locked. 

### Links for professor ratings?
- I scraped for RMP (Rate My Professor) links for all the UTD professors. Those links are shown in the Professor Information and Course Search features of the website.

### Grade Distribution for courses?
- A wonderful site called UTD grades shows grade distributions for courses. So, I added links to those grade distributions to the Course Search feature of the website.


**I made this website so it could provide some utility to students at UTD. The features are:**
- *Time Slots*: shows the time periods for when a room is open
- *Empty Rooms*: like Time Slots, but it is mainly for students who want to use a room for an exact amount of time
- *Room Schedule*: shows all the classes that will occur in given room for a particular day
- *Course Search*: displays all the section numbers for a class with the RateMyProf link and UTD Grades link, so it will help when figuring what classes to take 
- *Professor Information*: returns all the classes a professor is teaching and their RateMyProf link
- *Contact Me*: sends an email to utdRooms@gmail.com so I can try to provide feedback 

If you would like to see the process for this project: check out the. ipynb notebook or click [here](https://nbviewer.jupyter.org/github/mithil957/utdRooms/blob/master/courseBook.ipynb)

### Overview of the process:
  - UTD Coursebook has an advanced search feature with many filters. Clicking on these filters and searching will produced a 'URL' with a predictable pattern and the page will show a table with information we asked for. So, we generate all the possible URLs and scrape all data from the tables
    * Scraping all the data one by one would take a lot of time. So, I used threading to speed things up. 
  
  - Now we have all the data for every class taught at UTD for that semester. This data can then be manipulated by the functions created in the ipynb notebook. Those functions can then be used to make those features on the website.
  
Tools used: Python, Jupyter Notebook, Flask, HTML, CSS, Bootstrap 

I had a lot of fun making this tool and I learned a lot about web development and data scraping along the way. 



