import pygame
import math
import random

SIZE = (600,400) #pixel size of window

CAMPOS = 0 #camera position in mm, complex :)
ZOOM = 1 #mm per pixel

AIR = False

LINDRAG = .04
QUADRAG = .008

CLOSEMULT = .001
MAXCLOSE = 10

DEFAULTPATH = 'ocoTriCont.txt'

WHICHDRAW = (True,False,False) #whether to draw triangles, links, points

'''
Changed from 1.1: Added i and k controls to test future controls
'''

class World():

    def __init__(self,filename):
        
        self.size = SIZE

        self.cont = [ Jelly(filename) ]
        self.scenery = [ Floor(-150) ]

        self.zoom = ZOOM
        self.campos = CAMPOS

        pygame.init()
        self.screen = pygame.display.set_mode( self.size )


    def draw(self):

        self.screen.fill( (0,40,80) )

        for sce in self.scenery:
            sce.draw(self.screen, self)

        for obj in self.cont:
            obj.draw(self.screen, self)

        pygame.display.update()
            

    def frame(self):

        for obj in self.cont:
            obj.update()

        for obj in self.cont:
            obj.move()

        for obj in self.cont:
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
                force = (self.height - nodey)*.1
                force = force if force>-1 else -1
                #force = 1
                #node.pos -= force*1j
                node.pos = node.pos.real + self.height*1j
                #node.vel = 0
                node.vel = node.vel.real #+ force*1j

    def draw(self, surf, world):
        screenH = world.toScreen(self.height*1j)[1]
        pygame.draw.rect( surf, (255,200,100), (0,screenH,world.size[0],world.size[1]-screenH) )


class Jelly():

    def __init__(self,filename):

        self.nodes = [ Node(0,0) ]
        self.links = []
        self.tris = []

        self.controlNodes = { pygame.K_j:[n for n in self.nodes if n.control==pygame.K_j],
                              pygame.K_l:[n for n in self.nodes if n.control==pygame.K_l] }
        self.genJelly(filename)

    def genJelly(self,filename):

        self.nodes = []
        self.links = []

        with open(filename,'r') as theFile:
            part = 0
            for nextLine in theFile:
                nextLine = nextLine[:-1].split(' ')
                if nextLine==['']:
                    part = 1

                if part==0:                
                    x,y = int(nextLine.pop(0)),int(nextLine.pop(0))
                    newNode = Node(x+y*1j) 
                    self.nodes.append(newNode)

                    newNode.control = nextLine.pop(0)
                    if newNode.control: newNode.control = int(newNode.control)
                    
                    for connection in nextLine:
                        newLink = newNode.connect( self.nodes[int(connection)] )
                        self.links.append(newLink)

                if part==1 and not nextLine==['']:
                    p1,p2,p3,r,g,b = [int(thing) for thing in nextLine]
                    p1,p2,p3 = self.nodes[p1],self.nodes[p2],self.nodes[p3]
                    self.tris.append( Tri((p1,p2,p3),(r,g,b)) )
                    
    def draw(self,surf,world):

        toDraw = [ [self.tris,self.links,self.nodes][i] for i in range(3) if WHICHDRAW[i] ]
        #toDraw = (self.tris,)

        for thingList in toDraw:
            for thing in thingList:
                thing.draw(surf,world)


    def update(self):
        for link in self.links:
            link.pull()

        for i in range(len(self.nodes)):
            for j in range(i+1,len(self.nodes)):
                dis = self.nodes[i].pos - self.nodes[j].pos
                if abs(dis)<MAXCLOSE:
                    force = dis * (MAXCLOSE-abs(dis))**2 * CLOSEMULT
                    self.nodes[i].vel += force
                    self.nodes[j].vel -= force

        for node in self.nodes:
            node.update()

    def move(self):
        for node in self.nodes:
            node.move()
        

class Node():

    def __init__(self, pos, vel=0):
        self.pos = pos
        self.vel = vel
        self.connected = []
        self.control = ''

    def connect(self,other):
        self.connected.append( other )
        other.connected.append( self )
        return( Link(self,other) )

    def update(self):
        self.vel -= .3j * AIR
        drag = self.vel*LINDRAG + self.vel*abs(self.vel)*QUADRAG
        if False:
        #if abs(drag)>abs(self.vel):
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

        self.extMult = 1
        self.k = 0.0420
        
        self.length = length if length else abs(self.start.pos-self.end.pos)
        assert self.length>0

    def draw(self, surf, world):
        pygame.draw.line(surf,(255,255,255) ,world.toScreen(self.start.pos),world.toScreen(self.end.pos) )

    def pull(self):
        ext = abs(self.start.pos-self.end.pos) - self.length*self.extMult
        force = self.k * ext
        direction = (self.start.pos-self.end.pos)/abs(self.start.pos-self.end.pos)

        forceVector = force * direction
        #print(ext,force,direction,forceVector,'\n')
        self.start.vel -= forceVector
        self.end.vel   += forceVector


class Tri():

    def __init__( self, points, colour ):
        self.points = points
        self.colour = colour

    def draw(self, surf, world):
        pygame.draw.polygon(surf,self.colour, [world.toScreen(p.pos) for p in self.points] )
     

def main():

    filename = inputFile('.txt')
    
    world = World(filename)

    clock = pygame.time.Clock()
    running = True

    clicked = {0:0,1:0,2:0,'s':[],'d':[]}

    while running:

        clock.tick(30)

        running = handleEvents(world,clicked)
        if not running:
            break
        
        world.frame()
        world.draw()
        

    saveJelly(world)


def inputFile(filetype):
    from os import walk

    inDir = next(walk('C:/Users/Stazi/Google Drive/Sorted/Octopus'))[2]
    print('In directory:')
    for thing in inDir:
        if thing[-4:]==filetype:
            print(' -',thing)
    print()
    
    while True:
        inp = input('Enter filename to load or enter to select default: ')
        if not inp:
            return DEFAULTPATH
        if inp in inDir and inp[-4:]==filetype:
            return inp

def saveJelly(world):

    filename = input('Enter filename to save to or enter to not save: ')
    if not filename:
        return

    with open(filename,'w') as theFile:
        for i in range(len(world.cont[0].nodes)):
            node = world.cont[0].nodes[i]
            line = str(int(node.pos.real))+' '+str(int(node.pos.imag))

            line+=' '+str(node.control)

            for connected in node.connected:
                coni = world.cont[0].nodes.index(connected)
                if coni<i:
                    line += ' '+str(coni)

            theFile.write(line+'\n')
        theFile.write('\n')
        for tri in world.cont[0].tris:
            theFile.write( ' '.join([str(world.cont[0].nodes.index(n)) for n in tri.points])+' ' )
            theFile.write( ' '.join([str(n) for n in tri.colour])+'\n' )
                           
    



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
                            world.cont[0].links.append( closest.connect(clicked[2]) )
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
                global AIR
                AIR = not AIR
                
            if event.key == pygame.K_s:
                mx,my = pygame.mouse.get_pos()
                mousePos = world.fromScreen(mx,my)
                closest = min( world.cont[0].nodes, key = lambda n: abs(n.pos-mousePos) )
                clicked['s'].append( closest )

            if event.key == pygame.K_d:
                mx,my = pygame.mouse.get_pos()
                mousePos = world.fromScreen(mx,my)
                closest = min( world.cont[0].nodes, key = lambda n: abs(n.pos-mousePos) )
                clicked['d'].append( closest )

            
    keys = pygame.key.get_pressed()
    for link in world.cont[0].links:
        link.extMult = 1
    if keys[pygame.K_k]:
        for link in world.cont[0].links:
            link.extMult *= .7
    if keys[pygame.K_i]:
        for link in world.cont[0].links:
            link.extMult *= 1.5
    if keys[pygame.K_j]:
        for link in world.cont[0].controlNodes[pygame.K_j]:
            link.extMult *= 1.2
    if keys[pygame.K_l]:
        for link in world.cont[0].controlNodes[pygame.K_l]:
            link.extMult *= 1.5

        
                

    if clicked[0]:
        mx,my = pygame.mouse.get_pos()
        mousePos = world.fromScreen(mx,my)
        clicked[0].pos = mousePos
        clicked[0].vel = 0

    if len(clicked['s']) >= 3:
        r,g,b = random.randint(0,255),random.randint(0,255),random.randint(0,255)
        world.cont[0].tris.append( Tri( clicked['s'], (r,g,b) ) )
        clicked['s'] = []

    if len(clicked['d']) >= 2:
        for link in world.cont[0].links:
            if link.start in clicked['d'] and link.end in clicked['d']:
                world.cont[0].links.remove(link)
                link.start.connected.remove(link.end)
                link.end.connected.remove(link.start)
        clicked['d'] = []

    return True


if __name__ == '__main__':
    main()

    











      
