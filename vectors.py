import pygame, math as m, random, sys


class Body:
    def __init__(self, name, pos, mass, radius, initial_vel,path:list, img_file : str, keypos, ecc, sma,theta, colour = (255,255,255)):
        '''
        coontains all the attributes for a celestial body
        '''
        
        self.pos = pos #position of the body
        self.name = name #name of the body
        self.mass = mass #mass of the body 
        self.radius = radius #radius of the body (these are scaled for visibility)
        self.vel = initial_vel #initial velocity of the body
        self.path = path    #array of positions the body has taken
        self.img_file = img_file #sprite file for the body
        self.colour = colour #colour of the body's trail 
        self.keypos = keypos #position on the sidebar menu (y-coord)

        self.acc = Vector(0, 0) 
        self.jerk = Vector(0, 0)

        
        
        
        
        self.eccentricity = ecc
        self.semi_major_axis = sma
        
        self.theta = 0

     
    
    
    def draw(self, window: pygame.surface.Surface,res,physical_distance):
        '''
        draws the body onto the screen
        '''
        #pygame.draw.circle(window, self.colour,distance_conversion(res,self.pos,physical_distance), self.radius*res[0]/physical_distance) #change position to self.pos[:] if fails
        sprite = pygame.transform.scale(pygame.image.load(f'{self.img_file}'),(self.radius*res[0]*2/physical_distance,self.radius*res[1]*2/physical_distance))


        coord = ((distance_conversion(res,self.pos,physical_distance)[0] - self.radius*res[0]/physical_distance),(distance_conversion(res,self.pos,physical_distance)[1] - self.radius*res[0]/physical_distance))
        window.blit(sprite,coord)
    


class Vector:
    '''
    creates vector objects and holds Dunder methods for manipulating vectors
    '''
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)

    # Dunder methods
    def __repr__(self):
        '''
        Representation of Vector object used by jupyter
        '''
        return f"Vector({self.x}, {self.y})" 

    def __str__(self):
        '''
        returns a string from a vector 
        '''
        return f"({self.x}, {self.y})"  # When the vector is needed as a string, this format is used

    def __add__(self, other):
        '''
        adds 2 vectors
        '''
        return Vector(
            self.x + other.x, self.y + other.y
        )  

    def __sub__(self, other):
        '''
        subtracts 2 vectors
        '''
        return Vector(
            self.x - other.x, self.y - other.y
        )  

    def __getitem__(self, item):
        '''
        returns the components of a vector object
        '''
          # function to obtain a component of the vector object e.g (V(6,7,8)[0] = 6)
        return [self.x, self.y][item]

    def mag(self):
        return m.sqrt(
            self.x**2 + self.y**2
        )  # function to that returns the magnitude of a vector

    def scale(
        self, other
    ):  # function to scale a vector by either a scalar or another vector
        if type(other) == int or type(other) == float:
            return Vector(self.x * other, self.y * other)
        elif type(other) == Vector:
            return Vector(self.x * other.x, self.y * other.y)

    def dot(self, other):  # function to return the dot product of two vectors
        return (self.x * other.x) + (self.y * other.y)

    def norm(self):  # function to normalise a vector
        return self.scale(1 / self.mag())

    def dist(self, other):  # function to return the distance between two vectors
        return (self - other).mag()

    def gravForce(
        body_a, body_b, G
    ):  # Gravitational Force on body a as a result of body b
        rba = (body_b.pos - body_a.pos).mag()

        F =  G * body_a.mass * body_b.mass / rba**3

        return (body_b.pos - body_a.pos).scale(F)
    
    def gravForceRK(body_a, body_b, G, pos_a=None, pos_b=None):
        '''
        calculates the gravitational force between two objects for the Runge-Kutta method
        '''
        # Use provided override positions or default to the body's current position
        pos_a = pos_a if pos_a is not None else body_a.pos
        pos_b = pos_b if pos_b is not None else body_b.pos

        rba = (pos_b - pos_a).mag()
        if rba == 0:
            return Vector(0, 0)  # Prevent division by zero by returning zero vector
        F = G * body_a.mass * body_b.mass / rba**3
        return (pos_b - pos_a).scale(F)

    def netForceRK(target, bodies, G, pos_target=None):
        '''
        calculates the net force for the Runge-Kutta method
        '''
        cumulativeForce = Vector(0, 0)
        pos_target = pos_target if pos_target is not None else target.pos  # Use overridden position if provided
        for body in bodies:
            if body == target:
                continue
            # Calculate gravitational force using the current position of other bodies and the possibly overridden position of the target
            force = Vector.gravForceRK(target, body, G, pos_a=pos_target, pos_b=body.pos)
            cumulativeForce += force
        return cumulativeForce   

    def netForce(target, bodies, G): 
        '''
        sums the forces on an object
        '''
        cumulativeForce = Vector(0, 0)
        for body in bodies:
            if body == target:
                continue
            cumulativeForce += Vector.gravForce(target, body,G)
        return cumulativeForce
        
def distance_conversion(resolution, point, physical_distance):
        '''
        converts physical distances into pixel distances
        '''
        d_pixel_x = (physical_distance/resolution[0])
        d_pixel_y = (physical_distance/resolution[1])
        x_centre = resolution[0]/2
        y_centre = resolution[1]/2
        return (x_centre + point.x/d_pixel_y,y_centre + point.y/d_pixel_y)

def randomSeed(Bodies, simulation_distance,centre:int, Seednum):
    '''
    randomly generates initial positions and velocities for each planet
    '''
    for idx, body in enumerate(Bodies):
        if idx == centre:
            continue
        else:
            random.seed = Seednum

            vel_x = random.uniform(-1e2,1e2)
            vel_y = random.uniform(-1e2,1e2)

            pos_x = random.uniform(-1*simulation_distance/4, simulation_distance/4)
            pos_y = random.uniform(-1*simulation_distance/4, simulation_distance/4)

            body.initial_vel = Vector(vel_x, vel_y) #randomise velocity in m/s
            body.pos = Vector(pos_x, pos_y) #randomise position in relation to simulation distance