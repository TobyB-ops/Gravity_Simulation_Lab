#import necessary packages
import pygame, sys, ui, random
import numpy as np
from vectors import Body, Vector, distance_conversion, randomSeed
from enum import Enum
import math, pandas as pd, csv






class AppState(Enum):
    '''
    holds values for the different pages of the program
    '''
    INIT = 0
    EXIT = 1
    MENU = 2
    SIMULATION = 3
    SETTINGS = 4

class Method(Enum):
    '''
    holds values for the different propagation methods
    '''
    NONE = 0
    KEPLER = 1
    EULER = 2
    EULER_LEAPFROG = 3
    HERMITE = 4
    RUNGE_KUTTA = 5

class SeedState(Enum):
    '''
    holds values for different seeding options
    '''
    NONE = 0
    RANDOM = 1
    INPUT = 2



class App:
    '''
    holds the entire program. Functions update self attributes to affect the overall state of the simulation, 
    such as integration method or seed options
    '''
    def __init__(self, simsize: tuple[int, int], res):
        pygame.init()
        #globally checked attributes
        self.sim_time = 0 #time the simulation has ran for
        self.timescale = 50*86400 #time per frame (multiplier)

        self.clock = pygame.time.Clock()
        self.paused_clock = self.clock
        self.fixed_dt = False
        
        self.fps = 300 #number of seconds each frame represents
        self.simsize = simsize
        self.res = res
        self.window = pygame.display.set_mode(res)
        self.state = AppState.INIT #initial appstate
        self.bodies = [] 
        self.method = Method.NONE #defaults to no method 
        self.seed = SeedState.NONE #defaults to no seeding
        self.seed_num = 0 #seed used for randomisation
        self.user_text = '' #text stored by user
        self.simulation_distance = 1000e9#physical size of the simulation (m)
        self.kepler_count = 0 #counter for kepler method
        self.inner_planets = True

        self.data = []



        self.first_play = True 


        self.stars = [(random.randint(0, res[0]), random.randint(0, res[1])) for _ in range(100)]



        self.bodies = [
                Body( 'Sun', 
                Vector(0,0),1.989e30,696.3e7,Vector(0,0),[],'sun.png',200, 0, 0,0, pygame.color.THECOLORS['yellow'] #The Sun
                ),
                Body( 'Mercury', 
                    Vector(69.82e9,0),3.3e23,20000e6,Vector(0,38.86e3),[],'mercury.png', 250, 0.2056,57.9e9,0, pygame.color.THECOLORS['silver'] #Mercury
                ),
                Body( 'Venus', 
                    Vector(108.941e9,0),4.9e24,20000e6,Vector(0,34.78e3),[], 'venus.png', 300, 0.007,1.082e11, 0,pygame.color.THECOLORS['green'] #Venus
                ),
                Body( 'Earth',
                    Vector(152.100e9,0),6e24,20000e6,Vector(0,29.29e3),[], 'Earth.png',350, 0.017, 1.496e11,0,  pygame.color.THECOLORS['skyblue'] #Earth
                ),
            Body( 'Neptune',
                Vector(4.5588576e12,0),102e24,24764e6,Vector(0,5.370e3),[], 'neptune.png', 400, 0.009, 4.515e12, 0,pygame.color.THECOLORS['red'] #Mars
            ),
            Body( ' Mars',
                Vector(249.261e9,0),6.24e23,20000e6,Vector(0,21.97e3),[], 'mars.png', 450, 0.094, 2.28e11, 0, pygame.color.THECOLORS['gold'] #Mars
            ),
            Body( 'Saturn', 
                Vector(1506.527e9,0),568e24,60268e6,Vector(0,9.14e3),[],'saturn.png',500, 0.056, 1.432e12,0, pygame.color.THECOLORS['brown'] #Saturn
                ),
            Body( 'Jupiter', 
                Vector(816.363e9,0),1898e24,71492e6,Vector(0,12.44e3),[],'jupiter.png',550, 0.049, 7.785e11,0,pygame.color.THECOLORS['blueviolet']
                  #Jupiter
                ),

            Body('Uranus', 
                 Vector(3001.390e9,0), 86.8e24, 20000e6, Vector(0,6.490e3), [], 'uranus.png', 600,0.047, 2.867e12, 0,pygame.color.THECOLORS['cyan'] #uranus
                 
                 )

                ]   
        self.bodies_original = self.bodies

        #define menu buttons as pygame objects, updated by functions later on
        self.menu_items = [
            ui.Block(pygame.Rect(350, 75, 500, 75), "Gravity Simulation Lab", ui.buttonColour, ui.blockType.TITLE),

            ui.Button(pygame.Rect(950, 750, 200, 50),"QUIT", ui.buttonColour, ui.blockType.DEFAULT, self.exit,),

            ui.Button(
                pygame.Rect(400, 200, 400, 50),
                "Play",
                ui.buttonColour,
                ui.blockType.DEFAULT,
                self.play,
            ),
             ui.Button(
                pygame.Rect(400,300,400,50),
                "Settings",           
            ui.buttonColour,
            ui.blockType.DEFAULT,
                self.settings, 
            )

        ]  # objects on the setting menu screen
        self.settings_items = [
            ui.Block(pygame.Rect(350, 75, 500, 75), "Gravity Simulation Lab", ui.buttonColour, ui.blockType.TITLE),

            ui.Block(pygame.Rect(50, 200, 200, 50), "Seed & Size Options", ui.buttonColour, ui.blockType.DEFAULT), 

            ui.Button(pygame.Rect(50, 255, 120, 50), "Random Seed", ui.buttonColour, ui.blockType.SMALL, self.random_seed_button),

            ui.Button(pygame.Rect(200 ,255, 120, 50), "Input Seed", ui.buttonColour, ui.blockType.SMALL, self.input_seed_button),

            ui.Textbox(pygame.Rect(200, 315, 120, 50), "___", ui.buttonColour, ui.blockType.SMALL, self.input_seed_input_box, False),

            ui.Button(pygame.Rect(950, 750, 200, 50), "Back", ui.buttonColour, ui.blockType.DEFAULT, self.back),

            ui.Block(pygame.Rect(50, 400, 200, 50), "Method Options", ui.buttonColour, ui.blockType.DEFAULT),

            ui.Button(pygame.Rect(50, 455, 120, 50), "Euler", ui.buttonColour, ui.blockType.SMALL, self.euler), 

            ui.Button(pygame.Rect(200, 455, 120, 50), "Euler-leapfrog", ui.buttonColour, ui.blockType.SMALL, self.euler_leapfrog),

            ui.Button(pygame.Rect(350, 455, 120, 50), "Hermite", ui.buttonColour, ui.blockType.SMALL, self.hermite),

            ui.Button(pygame.Rect(500, 455, 120, 50), "Kepler", ui.buttonColour, ui.blockType.SMALL, self.kepler),

            ui.Button(pygame.Rect(650, 455, 120, 50), "Runge-Kutta", ui.buttonColour, ui.blockType.SMALL, self.runge_kutta)
         ]
        
        #menu options on the simulation sidebar
        self.sim_menu = [
            ui.Button(
                pygame.Rect(950, 750, 200, 50),
                "QUIT",
                ui.buttonColour,
                ui.blockType.DEFAULT,
                self.back,
                )
        ]
    
    def render_stars(self):
        '''
        "Render background stars"
        '''
        for star in self.stars:
            pygame.draw.circle(self.window, (255,255,255), star, 1)



    def initialise_sim(self, seedstate):
        '''
        initialises the simulation when the 'PLAY' button is pressed
        '''
        for body in self.bodies:
                body.path = []

        #if self.method == Method.KEPLER:
            
           # self.simulation_distance = self.simulation_distance
            #for body in self.bodies:
                #theta = np.linspace(0, 2*np.pi, 10000)
                #for i in range (0, len(theta)):
                  # r = body.semi_major_axis*(1 - body.eccentricity**2) / (1 + body.eccentricity*np.cos(theta[i]))
                   # body.path.append(Vector(r*np.cos(theta[i]), r*np.sin(theta[i])))
                #print(body.path)
                

        if seedstate != SeedState.NONE:
            if seedstate == SeedState.RANDOM:
                self.seed_num = random.randrange(sys.maxsize)
            if seedstate == SeedState.INPUT:
                self.seed_num = int(self.settings_items[4].text)
            randomSeed(self.bodies,self.simulation_distance,centre, self.seed_num)
            print(self.seed_num)
        self.sim_time = 0


   
   
   



    


    def update_position_kepler1(self,dt:float):


        self.sim_time += dt



        for body in self.bodies:
            if body == self.bodies[0]:
                continue
            else:
                "Update the position of the planet"
                
                k = 0.0172021 #kepler's gravitational constant
                
                body.theta += math.sqrt(6.67e-11 * (body.mass + self.bodies[0].mass) /(body.semi_major_axis) ** 3) * dt *(1/k)
                print(body.theta)               
                ang = math.radians(body.theta)



                r = body.semi_major_axis*(1-body.eccentricity**2)/(1+body.eccentricity*math.cos(ang))
                body.pos = Vector(r*math.cos(ang),r*math.sin(ang))
                body.path.append(body.pos)

                

                # Keep only the recent positions to avoid memory overload
                if len(body.path) > 5000:
                    del body.path[:-4000]







    def update_simulation_Euler(self, dt: float):
        '''
        propagates the simulation using Euler's numerical integration
        '''
        self.sim_time += dt



        for body in self.bodies:
                if distance_conversion(self.simsize, body.pos, self.simulation_distance)[0] > 900:
                    continue
                a = (Vector.netForce(body, self.bodies, 6.67e-11)).scale(
                    1
                    / body.mass  # calculate the acceleration on each body at each dt time step
                )
                body.vel = (a).scale(
                    dt
                ) + body.vel  # update the velocity vector of each body

                if body.vel.mag() > 3e8: #Highlights that the SOL has been exceeded 
                    print("physics has broken down!!!")

                body.pos = (
                    body.vel.scale(dt)
                    + body.pos  # update the position vector from the calculated velocity
                )

                body.path.append(body.pos) #add current position to the body's history of positions


                self.data.append({'Time': self.sim_time, 'Body': body.name, 'Position': body.pos.mag()})


    def update_simulation_leapfrog(self, dt: float):
            '''
            propagates the simulation using the Euler method with the leapfrog correction 
            '''
            self.sim_time += dt
            #times.append(self.sim_time)
    


            for body in self.bodies:
                if body == self.bodies[centre]:
                    continue
                else:
                    a_initial = (Vector.netForce(body, self.bodies, 6.67e-11)).scale(
                        1 / body.mass
                    )
                    body.vel = body.vel + a_initial.scale(dt / 2.0)  # Half-step update

            # Full-step for positions
            for body in self.bodies:
                if body == self.bodies[centre]:
                    continue
                else:
                    body.pos = body.pos + body.vel.scale(dt)
                    body.path.append(body.pos)  
                    self.data.append({'Time': self.sim_time, 'Body': body.name, 'Position': body.pos.mag()})

            # Second half-step for velocity
            for body in self.bodies:
                if body == self.bodies[centre]:
                    continue
                else:
                    a_final = (Vector.netForce(body, self.bodies, 6.67e-11)).scale(
                        1 / body.mass
                    )
                    body.vel = body.vel + a_final.scale(
                        dt / 2.0
                    )  # Completing the velocity update

                if body.vel.mag() > 3e8:
                    print("physics has broken down!!!")
                    
            for other in self.bodies:
                        if (
                            body == other
                        ):  # skip checking the current body with itself as this is unimportant
                            continue
                        elif body.pos.dist(other.pos) < (
                            body.radius + other.radius
                        ):  # Checks whether the current object is within the radius of the other objects (a collision has occured)
                            print(f"Objects have collided at {body.pos} and {other.pos}")
                    
            

    def update_simulation_hermite(self, dt: float):
        '''
        Propagates the simulation using Hermite integration, which includes a prediction,
        correction step using higher-order derivatives.
        '''
        
        G = 6.67e-11  # Gravitational constant
        self.sim_time += dt
        # Prediction step
        for body in self.bodies:
            body.pos_pred = body.pos + body.vel.scale(dt) + body.acc.scale(dt**2 / 2) + body.jerk.scale(dt**3 / 6)
            body.vel_pred = body.vel + body.acc.scale(dt) + body.jerk.scale(dt**2 / 2)

        # Update accelerations and jerks based on predicted positions
        for body in self.bodies:
            acc_new = Vector(0, 0)
            jerk_new = Vector(0, 0)
            for other_body in self.bodies:
                if body != other_body:
                    r_vec = other_body.pos_pred - body.pos_pred
                    r = r_vec.mag()
                    force_mag = G * body.mass * other_body.mass / r**3
                    force_vec = r_vec.scale(force_mag)

                    acc_new += force_vec.scale(1 / body.mass)

                    vel_diff = other_body.vel_pred - body.vel_pred
                    jerk_new += vel_diff.scale(force_mag / r).scale(1 / body.mass) - force_vec.scale(3 / r**2).scale((body.vel_pred - other_body.vel_pred).dot(r_vec) / body.mass)

            body.acc_new = acc_new
            body.jerk_new = jerk_new

        # Correction step
        for body in self.bodies:
            body.pos = body.pos_pred + (body.acc_new - body.acc).scale(dt**2 / 12) + (body.jerk_new - body.jerk).scale(dt**3 / 24)
            body.vel = body.vel_pred + (body.acc_new - body.acc).scale(dt / 2) + (body.jerk_new - body.jerk).scale(dt**2 / 12)

            # Update current acceleration and jerk to new values
            body.acc = body.acc_new
            body.jerk = body.jerk_new

            body.path.append(body.pos)  

            self.data.append({'Time': self.sim_time, 'Body': body.name, 'Position': body.pos.mag()})  # Tracking data

            
    def update_simulation_runge_kutta(self, dt :float):
        '''
        propagates the simulation using the runge kutta method, requires new net force function as the acceleration is recalculated at each interval
        '''                
        self.sim_time += dt
        G=6.67e-11
        for body in self.bodies:
            if body == self.bodies[centre]:
                continue
            else:

                 # Initial state
                initial_pos = body.pos
                initial_vel = body.vel

                 # First step
                a1 = Vector.netForceRK(body, self.bodies, G, pos_target = initial_pos).scale(1 / body.mass)
                v1 = body.vel
                p1 = body.vel.scale(dt)

                # Second step
                mid_vel = initial_vel + a1.scale(dt/2)
                a2 = Vector.netForceRK(body, self.bodies, G, pos_target=initial_pos + p1.scale(0.5)).scale(1 / body.mass)
                v2 = mid_vel
                p2 = mid_vel.scale(dt)

                # Third step
                mid_vel = initial_vel + a2.scale(dt/2)
                a3 = Vector.netForceRK(body, self.bodies, G, pos_target=initial_pos + p2.scale(0.5)).scale(1 / body.mass)
                v3 = mid_vel
                p3 = mid_vel.scale(dt)

                # Fourth step
                end_vel = initial_vel + a3.scale(dt)
                a4 = Vector.netForceRK(body, self.bodies, G, pos_target=initial_pos + p3).scale(1 / body.mass)
                v4 = end_vel
                p4 = end_vel.scale(dt)

                # Combine steps
                final_vel = initial_vel + (a1 + a2.scale(2) + a3.scale(2) + a4).scale(dt / 6)
                final_pos = initial_pos + (v1 + v2.scale(2) + v3.scale(2) + v4).scale(dt / 6)

                body.vel = final_vel
                body.pos = final_pos
                body.path.append(body.pos) 


                self.data.append({'Time': self.sim_time, 'Body': body.name, 'Position': body.pos.mag()}) 
                
                # Update the path for drawing           



    def run(self):
        '''
        runs the application in a loop, with events on click to affect change 
        '''
        self.state = AppState.MENU  # Start the Program in the menu
        
        while (
            self.state.value > AppState.EXIT.value
        ):  # Keep program running unless its closed

            pygame.display.update()
            self.window.fill(pygame.color.THECOLORS["black"])
            # due to objects constantly moving on the screen, they need to be reset in each frame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = AppState.EXIT
                    break  # Quit Option for the program (if something goes wrong)
                 # Check the state of the app (refer to AppState class)
                if app.state == AppState.MENU:  # when the AppState is menu
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            for block in self.menu_items:
                                if not isinstance(block, ui.Button):
                                    continue
                                if block.area.collidepoint(pygame.mouse.get_pos()):
                                    block.on_click()

                if app.state == AppState.SETTINGS:  # when the AppState is settings
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            for block in self.settings_items:
                                if not isinstance(block, ui.Button):
                                    continue
                                if block.area.collidepoint(pygame.mouse.get_pos()):
                                    block.on_click()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                                self.save_text()
                            elif event.key == pygame.K_BACKSPACE:
                                self.user_text = self.user_text[:-1] 
                            else:
                                self.user_text += event.unicode
  



                if app.state == AppState.SIMULATION:  # when the AppState is simulation
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            for block in self.sim_menu:
                                if not isinstance(block, ui.Button):
                                    continue
                                if block.area.collidepoint(pygame.mouse.get_pos()):
                                    block.on_click()
                        elif event.type == pygame.KEYDOWN:
                                if pygame.key.get_pressed()[pygame.K_s]:
                                    df = pd.DataFrame(self.data)
                                    df.to_csv(f'Radii_{self.method.name}.csv', index=False)
                                    print('times and positions saved successfully')
                                elif pygame.key.get_pressed()[pygame.K_t]:
                                    
                                    if self.inner_planets == True:
                                        self.simulation_distance *= 10
                                        self.inner_planets = False
                                    else:
                                        self.simulation_distance /= 10
                                        self.inner_planets = True


            

            if self.state is AppState.MENU:  # render menu
                self.window.blit(pygame.transform.scale(ui.BG, self.res), (0, 0))
                for block in self.menu_items:
                    block.draw(self.window)
                continue

            if self.state is AppState.SETTINGS:
                self.window.blit(pygame.transform.scale(ui.BG, self.res), (0, 0))
                for block in self.settings_items:
                    block.draw(self.window)
                continue 
            

            # Simulation:
            if self.state is AppState.SIMULATION:
                
                if self.method == Method.NONE:
                    self.back()

                #set font for sidebar key
                my_font = pygame.font.SysFont('Arial', 30)
                my_font_small = pygame.font.SysFont('Arial', 12)

                #draws sidebar elements that are constant, including seed
                pygame.draw.line(self.window, pygame.color.THECOLORS['white'], (900,0), (900,900), 10)

                timer = my_font_small.render(f'{self.sim_time/86400:.4f} days {self.sim_time:.4f} seconds ', True, (255,255,255))
                seed_text = my_font_small.render('Seed: '+ str(self.seed_num), False, pygame.color.THECOLORS["white"])
                self.window.blit(timer, (10,30))
                self.window.blit(seed_text, (950, 700))

                #draw sidebar menu
                for block in self.sim_menu:
                    block.draw(self.window)

                for body in self.bodies:  # render the simulation in each frame
                    
                    #draws the key panel 
                    key_text = my_font.render('Key:', False, pygame.color.THECOLORS["white"])
                    planet_text = my_font.render(body.name, False, pygame.color.THECOLORS["white"])
                    self.window.blit(planet_text, (1050,body.keypos - 18))
                    self.window.blit(key_text, (950, 150))
                    pygame.draw.circle(self.window, body.colour, (950,body.keypos), 10)
                    self.render_stars()

                    if len(body.path) > 2:
                        pygame.draw.lines(
                            self.window,
                            body.colour,
                            False,
                            [
                                distance_conversion(self.simsize, point, self.simulation_distance)
                                for point in body.path
                            ],
                            1,
                        )

                    if distance_conversion(self.simsize, body.pos, self.simulation_distance)[0] > 900:
                        continue
                    body.draw(self.window, self.simsize, self.simulation_distance)

                    

                #self.clock.tick(self.fps) / 1000 * self.timescale
                 # dt calculated as the time between each frame from the start of the simulation


                dt =(self.clock.tick(self.fps)-self.paused_clock.tick(self.fps)*self.fixed_dt)* self.timescale/ 1000


                if self.method == Method.KEPLER:
                    self.update_position_kepler1(dt)
                elif self.method ==  Method.EULER:
                    self.update_simulation_Euler(dt) 
                elif self.method == Method.EULER_LEAPFROG:
                    self.update_simulation_leapfrog(dt)
                elif self.method ==  Method.HERMITE:
                    self.update_simulation_hermite(dt) 
                elif self.method == Method.RUNGE_KUTTA:
                    self.update_simulation_runge_kutta(dt)    

                self.fixed_dt = False 

   
#main menu button functions
    def play(self): 
        '''
        sets the appstate to SIMULATION, and initialises the simulation 
        '''

      
        self.clock.tick()  # Reset the clock to discard any previous time accumulation
        
        self.state = AppState.SIMULATION
        self.initialise_sim(self.seed)  #change appstate to simulation - this will run the simulation


    def exit(self):
        '''
        sets the appstate to EXIT and closes the application
        '''
        self.state = AppState.EXIT #close the program

    def settings(self):
        '''
        sets the appstate to SETTINGS and sends user to the settings menu
        '''
        self.state = AppState.SETTINGS   

#settings menu button functions 
    def random_seed_button(self):
        '''
        randomises the initial positions and velocities of the planets
        '''
        if self.seed == SeedState.NONE:
            self.settings_items[2].color = pygame.color.THECOLORS["red"]
            self.seed = SeedState.RANDOM
        elif self.seed == SeedState.RANDOM:
            self.settings_items[2].color = ui.buttonColour
            self.seed = SeedState.NONE

    def input_seed_button(self):
        '''
        toggles the seed to be inputted instead of randomised
        '''
        if self.seed == SeedState.NONE:
            self.settings_items[3].color = pygame.color.THECOLORS["red"]
            self.seed = SeedState.INPUT
        elif self.seed == SeedState.INPUT:
            self.settings_items[3].color = ui.buttonColour
            self.seed = SeedState.NONE
        

    def input_seed_input_box(self):
        '''
        allows the user to input a seed number manually
        '''    
        self.settings_items[4].color = pygame.color.THECOLORS["red"]
        self.settings_items[4].text = ''
        self.settings_items[4].active = True      

    def back(self):
        ''''
        changes appstate to MENU and sends the user to the main menu 
        '''
        
        self.state = AppState.MENU

    def kepler(self):
        '''
        changes the active method to Keplerian elements
        '''
        if self.method == Method.NONE:
            self.settings_items[10].color = pygame.color.THECOLORS["red"]
            self.method = Method.KEPLER
        elif self.method == Method.KEPLER:
            self.settings_items[10].color = ui.buttonColour
            self.method = Method.NONE

    def euler(self):
        '''
        changes the active method to Euler integration
        '''
        if self.method == Method.NONE:
            self.settings_items[7].color = pygame.color.THECOLORS["red"]
            self.method = Method.EULER
        elif self.method == Method.EULER:
            self.settings_items[7].color = ui.buttonColour
            self.method = Method.NONE

    def euler_leapfrog(self):
        '''
        changes the active method to Euler integration with leapfrog corrections
        '''
        if self.method == Method.NONE:
            self.settings_items[8].color = pygame.color.THECOLORS["red"]
            self.method = Method.EULER_LEAPFROG
        elif self.method == Method.EULER_LEAPFROG:
            self.settings_items[8].color = ui.buttonColour
            self.method = Method.NONE

    def hermite(self):
        '''
        changes the active method to Hermite Gauss integration
        '''
        if self.method == Method.NONE:
            self.settings_items[9].color = pygame.color.THECOLORS["red"]
            self.method = Method.HERMITE
        elif self.method == Method.HERMITE:
            self.settings_items[9].color = ui.buttonColour
            self.method = Method.NONE    

    def runge_kutta(self):
        '''
        changes the active method to the Runge-Kutta algorithm 
        '''
        if self.method == Method.NONE:
            self.settings_items[11].color = pygame.color.THECOLORS["red"]
            self.method = Method.RUNGE_KUTTA
        elif self.method == Method.RUNGE_KUTTA:
            self.settings_items[11].color = ui.buttonColour
            self.method = Method.NONE    


            
    def save_text(self):
        '''
        changes the text of a textbox to what the user typed in (activates on RETURN press)
        '''
        for block in self.settings_items:
            if not isinstance(block, ui.Textbox):
                continue
            if block.active == True:
               block.text = self.user_text
               block.color = ui.buttonColour
               block.active = False
               self.user_text = ''
               

#variables for running
centre = 0
screen_size = (900,900)
app_size = (1200,900)
app = App(screen_size, app_size)
app.run()
inner_planets = True
times = []