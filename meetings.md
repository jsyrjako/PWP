# Meetings notes

## Meeting 1.
* **DATE: 30.1.2024**
* **ASSISTANTS: Mika Oja**

### Minutes
Meeting was 20 minutes long and there were no missing tasks. The project is on track. Design was sufficient.

### Action points
 - No action points were discussed.




## Meeting 2.
* **DATE: 16.2.2024**
* **ASSISTANTS: Mika Oja**

### Minutes
We were missing Flask run command from the README.
There might be too many models im the project and when implementing the project we should consider the amount of work that is needed to be done.
Comment model was not linked to the user model, this should be done.
Despite the sqlite3 database being used, the string(256) were used to store strings in the database. This should be changed to text type.
The project was named 'app' and it should be named differently to avoid confusion e.g. 'bikinghub'.


### Action points
 - Add Flask run command to the README.
 - Consider the amount of work that is needed to be done when implementing the models.
 - Link the comment model to the user model.
 - Change the string(256) to text type in the database.
 - Change the name of the project to avoid confusion.





## Meeting 3.
* **DATE: 20.3.2024**
* **ASSISTANTS: Mika Oja**

### Minutes
Meeting was 30 minutes long and there were minor problems.
The traffic and comment model was not implemented further due to the amount of work.
Url:s need to be changed to prular to avoid confusion.
MML API key need to be transferred to conf file and instance folder.Action needs to be removed.

### Action points
 - Remove instance folder.Action
 - MML API key to conf file or as an environmental variable.
 - Fix all Url:s to plurar like this /user/ -> /users/
 - Base ids -> e.g. UUID




## Meeting 4.
* **DATE: 10.4.2024**
* **ASSISTANTS: Mika Oja**

### Minutes
There was a connectedness issue in the link relations, there was no way to get back to UserItem or UserCollection from Favourites, Locations or Weathers.
Some bugs also arised when demoing the Swagger functionality.

### Action points
 - Custom link relation descriptions are missing.
 - Location is not standard.
 - Swagger didn't work properly.
 - Useritem and favourite cannot be accessed from location-tree




## Midterm meeting
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*




## Final meeting
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*




