Icon data json file source:

https://github.com/facundoolano/app-store-scraper/blob/master/README.md
In the above github link database, I downloaded 200 apps from each category and stored them as json files. Then these json files were merged and de-duplicated to get a json file containing 3300+ app icons and information.


About generating iPhone Screen:
https://github.com/WestYu531/Iphonescreen/blob/main/jsonscreen/screen3.py

In this github there is another folder is jsonscreen, in this folder is all the data and the final version of the program. category.js is to download the app information and save it in json format, combine.py is to check the files downloaded by category.js and merge them into a json file. and merge it into a json file. These two files do not need to run, because the final output json file is already contained in this folder (merged_unique_apps.json).

The name of the file that generates the final iPhone screen image is screen3.py. You need to change the path of the json file and the background image folder in main, and then you also need to change generateNum in main, which is the number of images generated for each background image. So the total number of background images generated will be (generateNum * number of background images). Before the program starts running, it will ask if you want to add the app name under the app icon. Just answer yes/no.

The final output will be the generated screen and json file. Below is an example of the output.
