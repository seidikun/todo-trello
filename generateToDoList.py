# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 23:42:45 2019

@author: seidi
"""

# Imports
import pandas as pd                        # To work with csv style sheet
import re                                  # Implements regular expression
from datetime import datetime, timedelta   # Time and period representations
from shutil import copyfile                # Does backup
from trello import TrelloClient            # Trello API

# Functions
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

# Initiate global variables
# Put your own paths here
# parentFolder is the folder where the excel is
# backupFolder is a place to copy importqant files (On my PC it is a one drive folder!)
parentFolder = 'C:\\Users\\seidi\\Documents\\(mapped) Important\\tutorial\\'
backupFolder = 'C:\\Users\\seidi\\Documents\\(mapped) Important\\tutorial\\backup\\'

# api and token found on https://trello.com/app-key. Copy and paste yours here
api_key    = 'e4ecded33d49181cf84f00dbdb4323d9'
api_secret = '5d23692536f273b4101351bc4d38aa11c32623bfcb5503c1130150f90abde721'
boardName  = 'TUTORIAL'

# =============================================================================
# Init Trello
# =============================================================================

# Access Trello client
client = TrelloClient(api_key, api_secret)

# Take all boards from current client
allBoards = client.list_boards()
allBoardsNames = []

# Acessing each board and making a list of names
for board in allBoards:
    allBoardsNames.append(board.name)

# Find ind of board
indBoardTODO = allBoardsNames.index(boardName)

# Get this board
boardTODO = allBoards[indBoardTODO]

# Board TODO is accessed, so take all lists
allLists = boardTODO.list_lists()

# Acessing each list and making a list of names
allListsNames= []
for currList in allLists:
    allListsNames.append(currList.name)
    
# Find ind of list with names 'TO DO', 'DOING' and 'DONE'
indListTODO  = allListsNames.index('TO DO')
indListDOING = allListsNames.index('DOING')
indListDONE  = allListsNames.index('DONE')

# Get this list
listTODO  = allLists[indListTODO]
listDOING = allLists[indListDOING]
listDONE  = allLists[indListDONE]
listTODO.archive_all_cards()
listDONE.archive_all_cards()

# Track which cards are on each list
# MAKE IT INTO A FUNCTION
allCardsDONE = listDONE.list_cards()
allCardsDONEStr = []
allCardsDONEDate = []
allCardsDONETaskNb = []
allCardsDONESubTask = []
for card in allCardsDONE:
  allCardsDONEStr.append(card.name)
  
  splitName = card.name.split('-')
  allCardsDONEDate.append(splitName[0].strip())
  
  TaskStr = re.findall('Task\d+',card.name)
  allCardsDONETaskNb.append(TaskStr[0])
  
  splitName = card.name.split(']')
  allCardsDONESubTask.append(splitName[-1].strip())
allCardsDONEStruct = [allCardsDONEStr, allCardsDONETaskNb, allCardsDONEDate, allCardsDONESubTask]

allCardsDOING = listDOING.list_cards()
allCardsDOINGStr = []
allCardsDOINGDate = []
allCardsDOINGTaskNb = []
allCardsDOINGSubTask = []
for card in allCardsDOING:
  allCardsDOINGStr.append(card.name)
  
  splitName = card.name.split('-')
  allCardsDOINGDate.append(splitName[0].strip())
  
  TaskStr = re.findall('Task\d+',card.name)
  allCardsDOINGTaskNb.append(TaskStr[0])
  
  splitName = card.name.split(']')
  allCardsDOINGSubTask.append(splitName[-1].strip())
allCardsDOINGStruct = [allCardsDOINGStr, allCardsDOINGTaskNb, allCardsDOINGDate, allCardsDOINGSubTask]

# =============================================================================
# Important variables go below
# =============================================================================

# Names of the days of the week
diaDaSemana  = ['Segunda-Feira','Terça-Feira','Quarta-Feira','Quinta-Feira','Sexta-Feira','Sábado','Domingo']
dayOfTheWeek = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturnday','Sunday']
dyenNedeli   = ['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота','Воскресенье']

# Formating varibales
messageRest = "[---- Rest (OR MOVE TASKS FOR TODAY) ----]"
maxWidthInCharacters = 98
underLineRep = '_'*45
centerSpacement = round((maxWidthInCharacters - len(messageRest))/2)

# Create period of time to do ToDo lists. Change here as needed
startDateLog = datetime(2019,6,25)
startDate    = datetime(2018,10,30)
endDate      = datetime(2019,10,25)
today        = datetime.now()

# Set Priority score. Values were found heuristically
lowPriorityScoreThresh    = 30
mediumPriorityScoreThresh = 50
highPriorityScoreThresh   = 60

# Read Events
eventsFilename = parentFolder + 'events.txt'
events         = pd.read_csv(eventsFilename, delimiter = ';')
eventsDates    = events['Date']
eventsNames    = events['Event']

# Open txt file to write bigToDoList
outputFilenameMain = parentFolder + 'DailyToDo.txt'
outputFileMain     = open(outputFilenameMain, 'w')

outputFilenameLate = parentFolder + 'DailyToDo_Late.txt'
outputFileLate     = open(outputFilenameLate, 'w')

# Main sheet
filename =  parentFolder + 'bigToDo.xlsx' # path to file + file name
sheet    =  'Everything' # sheet name or sheet number or list of sheet numbers and names

mainSheet = pd.read_excel(io=filename, sheet_name=sheet)

taskSheetName   = mainSheet['Task Nb']
taskTitles      = mainSheet['What']
taskDescription = mainSheet['Description']
taskDeadlineStr = mainSheet['Deadline']
taskScore       = mainSheet['Score']

taskSheetName = [x for x in taskSheetName if str(x) != 'nan']

taskSheet = {}

countWeeks = 1
for currentDate in daterange(startDate, endDate):
    nomeDoDia = diaDaSemana[currentDate.weekday()]
    dayName   = dayOfTheWeek[currentDate.weekday()]
    dyen      = dyenNedeli[currentDate.weekday()]
    
    hasEvent = False
    indexEvent = eventsDates[eventsDates == currentDate.strftime("%d/%m/%Y")].index
    if not indexEvent.empty:
        hasEvent = True
    
    # See if there is any event today
    if currentDate.weekday() == 0 and currentDate > startDateLog:  
        print(underLineRep, ' Week ', str(countWeeks), ' ', underLineRep, '\n\n\n', file = outputFileMain)
        countWeeks = countWeeks + 1
        
    # Entry for currentDate
    if currentDate > startDateLog:
      print('ToDo List Dia ', currentDate.strftime("%d/%m/%Y"), ' (', nomeDoDia, ')')
      print('>\nToDo List ', currentDate.strftime("%d/%m/%Y"), ' (',  dayName, '):\n', file = outputFileMain)
      cardName = currentDate.strftime("%d/%m/%Y") + ' - ' + dyen
      dueDate = currentDate.strftime("%Y/%m/%d")      
      position = 'top'          

    # Search in the whole excel file, and see which tasks are for today
    noTaskForToday = True
    for currentIndex in range(0,len(taskSheetName)):
        state = False
        taskName         = taskSheetName[currentIndex]
        scoreTask        = taskScore[currentIndex]
        sheetTaskVarName = "taskSheet['" + taskName + "']"
        
        if not taskName in taskSheet:
            taskSheet[taskName] = pd.read_excel(io=filename, sheet_name=taskName, header = 1,
                     converters = {'Time to Complete (h)':str}) # Read sheet ignoring first row 
        
        dates         = taskSheet[taskName]['Date']
        subTasks      = taskSheet[taskName]['What']
        checkTask     = taskSheet[taskName]['Check']
        timeToDo      = taskSheet[taskName]['Time to Complete (h)']
        scorePerTask  = taskSheet[taskName]['Score']
        
        if 'Review1' in  taskSheet[taskName]:
            reviewDates  = taskSheet[taskName]['Review1']
            idxReviewDate = reviewDates[reviewDates == currentDate].index
            
            for currentReview in range(0,len(idxReviewDate)):
              if len(taskSheetName[currentIndex]) == 5:
                  strToLog = '[' + taskSheetName[currentIndex] + '  - ' + taskTitles[currentIndex] + \
                  '] ' + subTasks[idxReviewDate[currentReview]]
              elif len(taskSheetName[currentIndex]) == 6:
                  strToLog = '[' + taskSheetName[currentIndex] + ' - ' + taskTitles[currentIndex] + \
                  '] ' + subTasks[idxReviewDate[currentReview]]
              
              if scoreTask < lowPriorityScoreThresh:
                  strToLog = '|+   | ' + strToLog
              elif scoreTask < mediumPriorityScoreThresh:
                  strToLog = '|++  | ' + strToLog
              elif scoreTask < highPriorityScoreThresh:
                  strToLog = '|+++ | ' + strToLog
              elif scoreTask > highPriorityScoreThresh:
                  strToLog = '|++++| ' + strToLog                  
                  
              if strToLog and currentDate > startDateLog:
                  strToLog = '[REVIEW]   ' + strToLog      
                  print(strToLog, file = outputFileMain)              
            
        indexDate = dates[dates == currentDate].index
        
        if not indexDate.empty:
            noTaskForToday = False
        
        for currentToDo in range(0,len(indexDate)):
            if len(taskSheetName[currentIndex]) == 5:
                strToLog = '(' + str(timeToDo[indexDate[currentToDo]]) +  'h)' + '[' + \
                taskSheetName[currentIndex] + '  - ' + taskTitles[currentIndex] + '] ' + \
                subTasks[indexDate[currentToDo]]
            elif len(taskSheetName[currentIndex]) == 6:
                strToLog = '(' + str(timeToDo[indexDate[currentToDo]]) +  'h)' + '[' + \
                taskSheetName[currentIndex] + ' - ' + taskTitles[currentIndex] + '] ' + \
                subTasks[indexDate[currentToDo]]
            
            if scoreTask < lowPriorityScoreThresh:
                strToLog = '|+   | ' + strToLog
            elif scoreTask < mediumPriorityScoreThresh:
                strToLog = '|++  | ' + strToLog
            elif scoreTask < highPriorityScoreThresh:
                strToLog = '|+++ | ' + strToLog
            elif scoreTask > highPriorityScoreThresh:
                strToLog = '|++++| ' + strToLog
                
            if checkTask[indexDate[currentToDo]] == 'OK':
                strToLog = '[DONE]     ' + strToLog
            elif checkTask[indexDate[currentToDo]] == 'Hiatus':
                strToLog = '[NOT YET]  ' + strToLog
            elif today > currentDate:
                strToLog = '[LATE!]    ' + strToLog 
                state = False
                                     
                print(currentDate.strftime("%d/%m/%Y"), '\n', strToLog, file = outputFileLate)
            else:
                strToLog = '        ' + strToLog
            
            if currentDate > startDateLog:
              print(strToLog, file = outputFileMain)  
              currCardName = cardName + ' - ' + strToLog
              if state:
                  newCard = listDONE.add_card(currCardName, desc = None, labels = None, 
                        due = dueDate, source = None, position = 'top')     
              else:                      
                  if(currCardName in allCardsDOINGStruct[0]):
                    print('\nCard not included in list DONE:')
                    print(currCardName)
                    pass
                  else:
                    newCard = listTODO.add_card(currCardName, desc = None, labels = None, 
                        due = dueDate, source = None, position = 'top') 
                         
    if noTaskForToday * (not hasEvent) and currentDate > startDateLog:
        print('\n' + ' '*centerSpacement + messageRest + ' '*centerSpacement + '\n', file = outputFileMain)
        
    elif hasEvent:
        strEvent = '[---- EVENT TODAY: ' +  events['Event'][indexEvent[0]] + ' ----]'
        centerSpacement = round((maxWidthInCharacters - len(strEvent))/2)
        print('\n' + ' '*centerSpacement + strEvent + ' '*centerSpacement + '\n',  file = outputFileMain)
            
    if currentDate > startDateLog:
      print('<\n', file = outputFileMain)
    
# Copy all important files to One Drive
copyfile(outputFilenameMain, backupFolder + 'DailyToDo.txt')
copyfile(outputFilenameLate, backupFolder + 'DailyToDo_Late.txt')
copyfile(eventsFilename, backupFolder + 'events.txt')
copyfile(parentFolder + 'bigToDo.xlsx' , backupFolder + 'bigToDo.xlsx')
  


    