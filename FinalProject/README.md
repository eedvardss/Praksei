# SS.LV HELPER
#### Video Demo:  <https://youtu.be/yzN2CYZhbM0?si=fRknqpS1xlfo7ncu>
#### Description:
We are two guys from Latvia. Edvards and Kristers. In Latvia there is this big online marketplace called ss.lv/ss.com and it has a lot of great features like filters, and a lot of categories, but in real estate category it lacks one important feature. It lacks a visual map view of all the estates in city. This feature would allow users to see listings more easily in their desired region. With this in mind, we created a website that scrapes data from SS.LV for flat listings, and shows them visually on a map.
It only shows listings for flats at this moment.

When going on our website, a register/login interface is shown. It was made to prevent people from spamming the site with unnecessary requests. The passwords are hashed using the werkzeug.security library, so no passwords are available to us and it ensures user safety.

The second part of the code is web-scraping. Using Apify services, we found already made SS.LV scraper that we utilized for our needs. Although the scraper works for both cars and real estates, our project only focused on real estate listings.

After SS.LV is scraped, we saved it to an JSON file using JSON library.

Using sqlite3 and SQL from CS50 library we imported the data into the already made real estate table in sqlite.

To show the listings on a map, we had to get geographical coordinates. By exporting the 'street' field values, we converted the street names to geographical coordinates using GOOGLE MAPS API. After getting the coordinates, they are imported into the real estate table next to their listings. This part of code was done in coordinates.py file, that was run right after /search function was done running using the subprocess library.

For showing markers with listings on a map, we used GOOGLE MAPS API again for maps embedding. To show information on the listings when a marker is clicked, an inbuilt fuction in the GOOGLE MAPS API was used - InfoWindow, here we imported the description of the listing, the URL to the original ss.lv site, and all the pictures.

In the making of this project, the knowledge we gained from cs50x introductory course helped us a lot. The finance assignment in week nine helped us a lot. The login and register with flask was a very crucial aspect of our project, and thanks to the finance assignment it was a lot easier to do it. Also the databases we learned to create using sqlite3 and manage with php helped, it was important for managing users and real estate data. The SQL was important for importing the data. Jinja was also helpful for making layouts of html's, and reusing it for similar templates.

We used a lot of languages in this project that we learned in this course, like SQL, Python, SQlite, HTML, CSS and Javascript.

One of the problems this program encounters is apify's api, which works 90% of time. The remaining 10% of time, it for some reason does not want to scrape the site, on the apify's dashboard it shows as succesful but it returns with 0 results. This might be also because ss.lv have some scraping detection methods, that stop this kind of action.
#   P r a k s e i  
 