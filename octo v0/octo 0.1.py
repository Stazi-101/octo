import pygame
import math

SIZE = (600,400) #pixel size of window

CAMPOS = 0 #camera position in mm, complex :)
ZOOM = 1 #mm per pixel

'''
Changed from 0.0: Added gravity, added handleEvents function
'''

class World():

    def __init__(self):
        
        self.size = SIZE

        self.cont = [ Jelly() ]
        self.scenery = [ Floor(-150) ]

        self.zoom = ZOOM
        self.campos = CAMPOS

        pygame.init()
        self.screen = pygame.display.set_mode( self.size )


    def draw(self):

        self.screen.fill( (0,0,0) )

        for obj in self.cont:
            obj.draw(self.screen, self)

        for sce in self.scenery:
            sce.draw(self.screen, self)

        pygame.display.update()
            

    def frame(self):

        for obj in self.cont:
            obj.update()
            for s in self.scenery:
                s.interact(obj)

        for obj in self.cont:
            obj.move()


    def toScreen(self, pos):
        relPos = pos - self.campos
        relPos/= self.zoom
        sx,sy = self.size[0]/2 + relPos.real , self.size[1]/2 - relPos.imag
        return int(sx),int(sy)


class Floor():

    def __init__(self, height):

        self.height = height


    def interact(self, jelly):

        for node in jelly.nodes:
            nodey = node.pos.imag
            if nodey < self.height:
                assert type(self.height) in (float,int) and type(nodey)in (float,int)
                force = (self.height - nodey)
                node.vel = node.vel.real + force*1j

    def draw(self, surf, world):
        screenH = world.toScreen(self.height*1j)[1]
        pygame.draw.rect( surf, (255,0,0), (0,screenH,world.size[0],world.size[1]-screenH) )


class Jelly():

    def __init__(self):

        self.nodes = []
        self.links = []
        
        self.genJelly()

    def genJelly(self):

        n1 = Node( -20+10j )
        n2 = Node(  0 +40j )
        n3 = Node(  20+20j )

        self.nodes.extend((n1,n2,n3))

        l1 = Link( n1,n2 )
        l2 = Link( n2,n3 )
        l3 = Link( n3,n1 )

        self.links.extend((l1,l2,l3))

    def draw(self,surf,world):

        for link in self.links:
            link.draw(surf,world)

        for node in self.nodes:
            node.draw(surf,world)

    def update(self):
        for link in self.links:
            link.pull()

        for node in self.nodes:
            node.update()

    def move(self):
        for node in self.nodes:
            node.move()
        

class Node():

    def __init__(self, pos, vel=0):
        self.pos = pos
        self.vel = vel

    def update(self):
        self.vel -= .05j
        self.vel *= .98

    def move(self):
        self.pos += self.vel

    def draw(self, surf, world):
        pygame.draw.circle(surf,(255,255,255), world.toScreen(self.pos), 3)


class Link():

    def __init__(self, start, end, length=0):

        self.start = start
        self.end = end

        self.k = .05
        
        self.length = length if length else abs(self.start.pos-self.end.pos)*1.2
        assert self.length>0

    def draw(self, surf, world):
        pygame.draw.line(surf,(255,0,255) ,world.toScreen(self.start.pos),world.toScreen(self.end.pos) )

    def pull(self):
        ext = abs(self.start.pos-self.end.pos) - self.length
        force = self.k * ext
        direction = (self.start.pos-self.end.pos)/abs(self.start.pos-self.end.pos)

        forceVector = force * direction
        #print(ext,force,direction,forceVector,'\n')
        self.start.vel -= forceVector
        self.end.vel   += forceVector
        



def main():
    world = World()

    clock = pygame.time.Clock()
    running = True

    while running:

        clock.tick(30)

        world.frame()
        world.draw()

        running = handleEvents(world)

def handleEvents(world):
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return False

    return True


if __name__ == '__main__':
    main()

    











      
