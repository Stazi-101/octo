import pygame
import math

SIZE = (600,400) #pixel size of window

CAMPOS = 0 #camera position in mm, complex :)
ZOOM = 1 #mm per pixel

GRAV = False

LINDRAG = .02
QUADRAG = .003

'''
Changed from 0.3: Added linear and quadratic drag
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

        for sce in self.scenery:
            sce.draw(self.screen, self)

        for obj in self.cont:
            obj.draw(self.screen, self)

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


    def fromScreen(self, sx,sy):
        relX = sx - self.size[0]/2
        relY = self.size[1]/2 - sy
        relPos = complex(relX,relY)
        relPos *= self.zoom
        relPos += self.campos
        return relPos


class Floor():

    def __init__(self, height):

        self.height = height


    def interact(self, jelly):

        for node in jelly.nodes:
            nodey = node.pos.imag
            if nodey < self.height:
                force = (self.height - nodey)
                force = force if force>-1 else -1
                #force = 1
                #node.pos -= force*1j
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

        self.nodes.extend((n1,))

        l1 = Link( n1,n2 )
        l2 = Link( n2,n3 )
        l3 = Link( n3,n1 )

        #self.links.extend((l1,l2,l3))

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
        self.vel -= .5j * GRAV
        drag = self.vel*LINDRAG + self.vel*abs(self.vel)*QUADRAG
        if abs(drag)>abs(self.vel):
            self.vel = 0
        else:
            self.vel -= drag

    def move(self):
        self.pos += self.vel

    def draw(self, surf, world):
        pygame.draw.circle(surf,(255,255,255), world.toScreen(self.pos), 3)


class Link():

    def __init__(self, start, end, length=0):

        self.start = start
        self.end = end

        self.k = .2
        
        self.length = length if length else abs(self.start.pos-self.end.pos)
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

    clicked = {0:0,1:0,2:0}

    while running:

        clock.tick(30)

        world.frame()
        world.draw()

        running = handleEvents(world,clicked)


def handleEvents(world,clicked):
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if pygame.mouse.get_pressed()[2]:
                mx,my = pygame.mouse.get_pos()
                mousePos = world.fromScreen(mx,my)

                closest = min( world.cont[0].nodes, key = lambda n: abs(n.pos-mousePos) )
                closestDis = abs(closest.pos-mousePos)
                if closestDis > 20:
                    world.cont[0].nodes.append( Node(mousePos) )
                else:
                    if clicked[2]:
                        if clicked[2] != closest:
                            world.cont[0].links.append( Link( closest, clicked[2] ) )
                        clicked[2]=0
                    else:
                        clicked[2]=closest

                

            elif pygame.mouse.get_pressed()[0]:
                mx,my = pygame.mouse.get_pos()
                mousePos = world.fromScreen(mx,my)
                closest = min( world.cont[0].nodes, key = lambda n: abs(n.pos-mousePos) )
                
                clicked[0]=closest
                

        elif event.type == pygame.MOUSEBUTTONUP:
            clicked[0]=0

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                global GRAV
                GRAV = not GRAV

    if clicked[0]:
        mx,my = pygame.mouse.get_pos()
        mousePos = world.fromScreen(mx,my)
        clicked[0].pos = mousePos
        clicked[0].vel = 0
    '''
    if pygame.mouse.get_pressed()[0]:
        mx,my = pygame.mouse.get_pos()
        mousePos = world.fromScreen(mx,my)
        closest = min( world.cont[0].nodes, key = lambda n: abs(n.pos-mousePos) )
        closest.pos = mousePos
        closest.vel = 0
    '''
    return True


if __name__ == '__main__':
    main()

    











      
