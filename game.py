import sys, pygame, random, json
import framework as fw
import textwrapping as tw
pygame.init()

SIZE = WIDTH, HEIGHT = 400, 440
FPS = 40
ROOM_FONT = pygame.font.SysFont('Tahoma', 11)
UI_FONT = pygame.font.SysFont('Tahoma',15)
clock = pygame.time.Clock()
screen = pygame.display.set_mode(SIZE)
# pylint: disable=E1121,E1123
worldScreen = pygame.Surface(SIZE,flags=pygame.SRCALPHA)
worldRect = worldScreen.get_rect()
# pylint: disable=E1121,E1123
uiScreen = pygame.Surface(SIZE,flags=pygame.SRCALPHA)
uiRect = uiScreen.get_rect()
pygame.display.set_caption('Mystery')

IMG_PERSON_BORDER = pygame.image.load('img/person-background.png')
IMG_PERSON_BORDER_HIGHLIGHTED = pygame.image.load('img/person-background-highlighted.png')

class Person(pygame.sprite.Sprite):
    def __init__(self, person, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.person = person
        # pylint: disable=E1121,E1123
        self.image = pygame.Surface((22,22),flags=pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x - 1, y - 1

        if(self.person.alive):
            self.foreground = pygame.image.load('img/' + person.name + '.png')
        else:
            self.foreground = pygame.Surface((1,1),flags=pygame.SRCALPHA)
        self.foregroundRect = self.foreground.get_rect(center=(self.rect.width/2,self.rect.height/2))

        self.background = IMG_PERSON_BORDER
        self.backgroundRect = self.background.get_rect(center=(self.rect.width/2,self.rect.height/2))

        self.updateImage()
    
    def update(self):
        self.updateImage()
    
    def updateImage(self):
        self.image.fill((255,255,255,0))
        self.image.blit(self.background,self.backgroundRect)
        self.image.blit(self.foreground,self.foregroundRect)

    def highlight(self):
        self.background = IMG_PERSON_BORDER_HIGHLIGHTED
    
    def removeHighlight(self):
        self.background = IMG_PERSON_BORDER


class Room(pygame.sprite.Sprite):
    def __init__(self,room, x, y, width=100, height=100):
        pygame.sprite.Sprite.__init__(self)
        self.room = room
        self.image = pygame.Surface((width,height))
        self.image.fill((180,180,180))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

        swapToAltImage = False
        if self.rect.x % 200 != 0:
            swapToAltImage = True
        if self.rect.y % 200 != 0:
            swapToAltImage = not swapToAltImage
        
        if swapToAltImage:
            self.image.fill((150,150,150))

        textSurf = ROOM_FONT.render(self.room.name, 1, (0,0,0))
        textRect = textSurf.get_rect(center=(self.rect.width/2, self.rect.height/2))
        self.image.blit(textSurf, textRect)

class UIText(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,text):
        pygame.sprite.Sprite.__init__(self)

        self.text = text
        self.textWrapped = tw.wrapline(text,UI_FONT,width - 20)
        # pylint: disable=E1121
        self.image = pygame.Surface((width,height))
        self.rect = self.image.get_rect(x=x,y=y)

        self.buildText()

    def buildText(self):
        self.image.fill((255,255,255))
        for para in range(len(self.textWrapped)): #   0    1      #  len = 2
            thisText = UI_FONT.render(self.textWrapped[para],1,(0,0,0))
            thisRect = thisText.get_rect()
            if len(self.textWrapped) == 1:
                thisRect.center = [self.rect.width/2,self.rect.height/2 + (para * 20)]
            else:
                thisRect.center = [self.rect.width/2,self.rect.height/2 - (float(len(self.textWrapped))/2 * 10) + (para * 20)]
            self.image.blit(thisText,thisRect)


    def updateText(self,text):
        self.text = text
        self.textWrapped = tw.wrapline(text,UI_FONT,self.rect.width - 20)
        self.buildText()
    
    def hideText(self):
        self.image.set_alpha(0)
    
    def showText(self):
        self.image.set_alpha(255)

class Button(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,text,clicked):
        pygame.sprite.Sprite.__init__(self)

        # pylint: disable=E1121
        self.image = pygame.Surface((width,height))
        self.rect = self.image.get_rect(x=x,y=y)

        self.text = text
        self.clicked = clicked

        self.buildText()
    
    def buildText(self):
        self.textSurf = UI_FONT.render(self.text,1,(0,0,0))
        self.textRect = self.textSurf.get_rect()
        self.textRect.center = [self.rect.width/2,self.rect.height/2]

        self.image.fill((180,180,180))
        self.image.blit(self.textSurf,self.textRect)

    def update(self):
        mx, my = pygame.mouse.get_pos()

        if self.rect.collidepoint((mx,my)):
            self.image.fill((190,190,190))
        else:
            self.image.fill((180,180,180))
        
        self.image.blit(self.textSurf,self.textRect)


class ActionToggle(pygame.sprite.Sprite):
    canShowQuestionMark = True

    def __init__(self,x,y,width,height,options):
        pygame.sprite.Sprite.__init__(self)
        self.options = options
        self.index = 0

        # pylint: disable=E1121
        self.image = pygame.Surface((width,height))
        self.rect = self.image.get_rect(x=x,y=y)

        self.buildText()
    
    def buildText(self):
        self.textSurf = UI_FONT.render(self.options[self.index],1,(0,0,0))
        self.textRect = self.textSurf.get_rect()
        self.textRect.center = [self.rect.width/2,self.rect.height/2]

        self.image.fill((255,255,255))
        self.image.blit(self.textSurf,self.textRect)

    def update(self):
        mx, my = pygame.mouse.get_pos()

        if self.rect.collidepoint((mx,my)):
            self.image.fill((230,230,230))
        else:
            self.image.fill((220,220,220))
        
        self.image.blit(self.textSurf,self.textRect)
    
    def clicked(self):
        if self.options[self.index] == '?':
            ActionToggle.canShowQuestionMark = True
        elif self.index + 1 < len(self.options):
            if self.options[self.index + 1] == '?':
                if ActionToggle.canShowQuestionMark:
                    ActionToggle.canShowQuestionMark = False
                else:
                    self.index += 1

        
        self.index += 1
        if self.index >= len(self.options):
            self.index = 0
        
        self.buildText()


peopleGroup = pygame.sprite.Group()
roomGroup = pygame.sprite.Group()
uiGroup = pygame.sprite.Group()

defaultDialogGroup = pygame.sprite.Group()
choiceDialogGroup = pygame.sprite.Group()
resultDialogGroup = pygame.sprite.Group()

personInputList = []
roomInputList = []

game = fw.Game([
    fw.Room('DINING ROOM'),
    fw.Room('LIBRARY'),
    fw.Room('KITCHEN'),
    fw.Room('BEDROOM'),
    fw.Room('LOUNGE'),
    fw.Room('STUDY'),
    fw.Room('HALL'),
    fw.Room('BALLROOM')
],[
    fw.Person('MUSTARD'),
    fw.Person('BLUE'),
    fw.Person('SCARLET'),
    fw.Person('NAVY'),
    fw.Person('GREEN')
])

rx = 0
ry = 0
for room in game.rooms:
    roomSprite = Room(room,rx,ry)
    roomGroup.add(roomSprite)

    rx += 100
    if rx >= WIDTH:
        ry += 100
        rx = 0
    
    roomInputList.append(room.name)


for person in game.people:
    px = 300
    py = 300
    for roomSprite in roomGroup:
        for p2 in roomSprite.room.people:
            if p2['name'] == person.name:
                px = random.randrange(roomSprite.rect.x,roomSprite.rect.x + roomSprite.rect.width - 20)
                py = random.randrange(roomSprite.rect.y,roomSprite.rect.y + roomSprite.rect.height - 20)
    
    personSprite = Person(person, px, py)
    peopleGroup.add(personSprite)

    personInputList.append(person.name)

personChoiceButton = ActionToggle(0,HEIGHT-200,WIDTH,40,personInputList + ['?'])
choiceDialogGroup.add(personChoiceButton)
actionChoiceButton = ActionToggle(0,HEIGHT-160,WIDTH,40,['ENTER','IN','LEAVE'] + ['?'])
choiceDialogGroup.add(actionChoiceButton)
placeChoiceButton = ActionToggle(0,HEIGHT-120,WIDTH,40,roomInputList + ['?'])
choiceDialogGroup.add(placeChoiceButton)
timeChoiceButton = ActionToggle(0,HEIGHT-80,WIDTH,40,[str(x * 0.5) for x in range(2, 21)] + ['?'])
choiceDialogGroup.add(timeChoiceButton)

talkingToText = UIText(0,HEIGHT-240,WIDTH,40,'')
choiceDialogGroup.add(talkingToText)
tipText = UIText(0,HEIGHT-240,WIDTH,240,'Click on somebody to interact with them.')
defaultDialogGroup.add(tipText)
resultText = UIText(0,HEIGHT-240,WIDTH,240,'You shouldn\'t see this.')
resultDialogGroup.add(resultText)

selectedPerson = None
dialogShown = 'DEFAULT'

def onEnterButtonClicked(self):
    global selectedPerson, dialogShown

    if ActionToggle.canShowQuestionMark == True:
        return

    asking = selectedPerson.person
    who = personChoiceButton.options[personChoiceButton.index]
    what = actionChoiceButton.options[actionChoiceButton.index]
    where = placeChoiceButton.options[placeChoiceButton.index]
    when = timeChoiceButton.options[timeChoiceButton.index]

    result = fw.askPerson(asking.memory,asking.name,who,what,where,when)

    
    selectedPerson.removeHighlight()
    selectedPerson = None
    
    talkingToText.updateText('You shouldn\'t see this.')
    resultText.updateText(fw.handleResult(result,asking.name,who,what,where,when))
    dialogShown = 'RESULT'

enterButton = Button(0,HEIGHT-40,WIDTH,40,'Ask',onEnterButtonClicked)
choiceDialogGroup.add(enterButton)

print(game.murderer.name + ' killed ' + game.target.name)

while 1:
    choiceDialogGroup.update()
    uiGroup.update()
    peopleGroup.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONUP:
            mx, my = pygame.mouse.get_pos()
            for personSprite in peopleGroup:
                if personSprite.rect.collidepoint((mx,my)):
                    if personSprite.person.alive:
                        talkingToText.updateText('You are talking to ' + personSprite.person.name)
                        dialogShown = 'CHOICE'
                        if selectedPerson is not None:
                            selectedPerson.removeHighlight()
                        personSprite.highlight()
                        selectedPerson = personSprite
                    else:
                        resultText.updateText(personSprite.person.name + ' is dead.')
                        personSprite.highlight()
                        selectedPerson = personSprite
                        dialogShown = 'RESULT'
            if dialogShown == 'CHOICE':
                for choiceSprite in choiceDialogGroup:
                    if type(choiceSprite) == ActionToggle and choiceSprite.rect.collidepoint((mx,my)):
                        choiceSprite.clicked()
                if enterButton.rect.collidepoint((mx,my)):
                    enterButton.clicked(enterButton)
            elif dialogShown == 'RESULT':
                if resultText.rect.collidepoint((mx,my)):
                    dialogShown = 'DEFAULT'
                    if selectedPerson is not None:
                        selectedPerson.removeHighlight()
                    selectedPerson = None
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and dialogShown == 'RESULT':
                dialogShown = 'DEFAULT'
                


    screen.fill((255,255,255))
    worldScreen.fill((255,255,255,0))
    uiScreen.fill((255,255,255,0))

    roomGroup.draw(worldScreen)
    peopleGroup.draw(worldScreen)
    if(dialogShown == 'CHOICE'):
        choiceDialogGroup.draw(uiScreen)
    elif(dialogShown == 'RESULT'):
        resultDialogGroup.draw(uiScreen)
    else:
        defaultDialogGroup.draw(uiScreen)
    uiGroup.draw(uiScreen)
    screen.blit(worldScreen,worldRect)
    screen.blit(uiScreen,uiRect)
    pygame.display.flip()