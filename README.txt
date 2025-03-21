Gravity Simulation Lab by Gravity Delta

------------
Installation
------------

To install and run the project, simply download the repository from the Cocalc project, including the appropriate sprites.
Note that the project must be run locally at not in a Juypter environment.

To run the program, run main.py. Before attempting to run main.py, several external packages are required which are not included in the repository,
which can be installed using pip commands. These are the relevant packages:
- pygame
- random
- numpy
- enum 

------------
  Running
------------

The program is designed to run solely within a separately created window and so terminal input is not required whilst the project is running. 
Pressing 'Quit' will close this window and therefore the program. To run a simulation, a method must first be selected from the settings menu, otherwise the simulation will stutter and return to the main menu.
Unless a seed option is selected, the simulation will run using NASA measurements as the initial conditions. Selecting random seed will causes the simulation to be loaded using the system time as the seed. 
Selecting input seed toggles the program to use whatever value is held in the textbox beneath as the seed, which has '___' as a placeholder.
To overwrite this simply click the textbox and enter an integer value, pressing enter saves the text. Running the simulation
with non-integer values can cause crashes.
The only exception to this is the Kepler method, which does not use initial conditions and therefore is not affected by seed options. 
Selecting these options will not prevent the simulation being ran with the Kepler method.
Pressing 'back' from the simulation will return a user to the main menu and reset the simulation. If using a random seed, the seed will be different upon restsrting the animation.
Whilst an animation is running, press S to save the animation as a csv file, press T to switch between the inner and outer planets view.






 


   