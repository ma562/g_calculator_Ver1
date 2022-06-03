################################################################################
# Author: Joseph Ma
# Date: 01/17/2021
# Update: 03/13/2021 | Enables user to analyze multiple files without rerunning program
# Update: 11/24/2021 |  Makes score weightage in relative to each other
################################################################################
from matplotlib.widgets import Slider
import numpy as np
import matplotlib.pyplot as plt
#***********************************COURSE CLASS***********************************
#Description: Stores information regarding the entire course
#**********************************************************************************
class Course:
    def __init__(self, name, numCategories):
        self.name = name                        #name of course
        self.numCategories = numCategories      #number of categories in course
        self.gradeScale = []                    #list holding the grade scale 
        self.categories = []                    #list holding the categories

    def addCategory(self, category):
        self.categories.append(category)
        
    def addGrade(self, theGrade):
        self.gradeScale.append(theGrade)

    def categoryByIndex(self, index):
        return self.categories[index]

#***********************************CATEGORY CLASS***********************************
#Description: Stores information regarding each course grading category.
#************************************************************************************
class Category:
    def __init__(self, name, weighting, numAssessments, maxPtsEach):
        self.name = name                        #name of category
        self.weighting = weighting              #category weighting in percent
        self.numAssessments = numAssessments    #number of assessments within category
        self.maxPtsEach = maxPtsEach            #maximum points on each assessment
        self.scores = []                        #list holding user's scores
        self.completion = False
        self.total = 0

    def addScore(self, score):
        self.scores.append(score)

    def setCompletion(self, completeness):
        self.completion = completeness

    def getNumCompleted(self):
        return len(self.scores)

    def getPtsEarnt(self):
        for x in range(len(self.scores)):
            self.total += self.scores[x]
        return self.total  #returns the sum of scores earnt

    def getInfluence(self):         
        influenceLeft = self.weighting * (1 - len(self.scores) / self.numAssessments)
        return influenceLeft
        
#***********************************GRADE CLASS***********************************
#Description: Stores information regarding a letter and cutoff.
#*********************************************************************************
    
class Grade:
    def __init__(self, letter, cutOff):
        self.letter = letter        #Letter 
        self.cutOff = cutOff        #Cutoff percentage
    
#***********************************MAINDATA CLASS***********************************
#Description: Stores information regarding the entire course progress
#************************************************************************************
    
class mainData:
    def __init__(self, current, possible, loss, final, progress):
        self.current = current          #Current earnings in percentage
        self.possible = possible        #Percent user had the opportunity to earn
        self.loss = loss                #Percent user permanently lost
        self.final = final              #Percent course final points out of
        self.progress = progress        #User's percent progress so far

    def getHighest(self):
        return self.final - self.loss

#***********************************GRAPHER CLASS***********************************
#Description: Stores information necessary for graphing
#************************************************************************************

class grapher:
    def __init__(self):
        self.cutOff = []
        self.letter = []
        self.category = []
        self.sliders = []
        self.sliderVals = []
        self.influence = []
        self.sliderNum = 0
        self.earned = 0

    def addCutOff(self, grade):
        self.cutOff.append(grade)

    def addLetter(self, grade):
        self.letter.append(grade)

    def addCategory(self, theCategory):
        self.category.append(theCategory)

    def addSlider(self, slider, influence):
        self.sliders.append(slider)
        self.influence.append(influence)
    
    def setGraphInfo(self, num, earned):
        self.SliderNum = num
        self.earned = earned
        
    def updateGraph(self, val):
        theTotal = 0
        maxPercentEarn = 0
        for x in range(self.SliderNum):
            theTotal += self.sliders[x].val * self.influence[x] / 100
            maxPercentEarn += self.influence[x]

        x = theTotal * 100 / maxPercentEarn
        y = theTotal + self.earned
        gradePlotX.set_xdata(x)     #update graph 
        gradePlotY.set_ydata(y)
        
#***********************************MAIN FUNCTION***********************************
#Description: Directs the program
#***********************************************************************************
        
def main():
    go = True

    while(go):
        data = readFile()
        theCourse = interpretData(data)   #check what is returned
        while(theCourse == False):
            print("Please review text file formatting...")
            print("Update file, save and re-enter file name for review")
            data = readFile()
            theCourse = interpretData(data)   #check what is returned

        courseData = scale(theCourse)
        courseData = dataCalculator(theCourse)
        mainDataCalculator(courseData, theCourse)
        graph(courseData, theCourse)

        cont = input("Would you like to read another file? (y/n): ")
        if(cont.lower()[0] == 'n'):
            go = False

#***********************************SCALE DATA***********************************
#Description: Scales the input weightages in relation to each other
#************************************************************************************
def scale(course):
    total_weights = 0
    for c in range(course.numCategories):
        total_weights += course.categoryByIndex(c).weighting
    for c in range(course.numCategories):
        course.categoryByIndex(c).weighting /= total_weights
        course.categoryByIndex(c).weighting *= 100
    return course


#***********************************GRAPH FUNCTION***********************************
#Description: Graphs information and provides sliders to manipulate variables
#************************************************************************************
    
def graph(mainData, course):
    if(abs(mainData.possible - 100) < 0.0001):
        #grade is determined already -> There are no more variables for sliders
        return False
    
    ourGrade = 0
    maxGrade = 0
    
    theGraph = grapher()    #creates theGraph object
    
    #Find the current spot in the grade scale
    for x in range(len(course.gradeScale)):
        
        cutOff = float(course.gradeScale[x].cutOff)
        cutOff -= float(mainData.current)
        cutOff *= 100 / (100 - mainData.possible)
        
        if(maxGrade == 0 and cutOff <= 100):
            maxGrade = course.gradeScale[x]
            
        if(x < (len(course.gradeScale) - 1)):
            topCutOff = float(course.gradeScale[x].cutOff)
            bottomCutOff = float(course.gradeScale[x + 1].cutOff)
            if(mainData.current < topCutOff and mainData.current >= bottomCutOff):
                ourGrade = course.gradeScale[x + 1]
        else:
            if(ourGrade == 0):
                ourGrade = course.gradeScale[x]
            if(maxGrade == 0):
                maxGrade = course.gradeScale[x]

        if(cutOff <= 100 and cutOff >= 0):
            theGraph.addCutOff(course.gradeScale[x].cutOff)
            theGraph.addLetter(course.gradeScale[x].letter + " (" + str(course.gradeScale[x].cutOff) + "%)")

    theGraph.addCutOff(mainData.current)
    theGraph.addLetter("Earned: " + str(round(mainData.current, 2)) + "%")
    
    #number of SLIDERS
    sliders = []
    numSliders = 0
    for x in range(course.numCategories):
        if(course.categoryByIndex(x).completion != True):
            theGraph.addCategory(course.categoryByIndex(x))
            numSliders += 1

    #general plot layout
    #first index- where plot begins on x-axis
    #second index- where plot begins on y-axis
    #third index- length of plot
    #fourth index- height of plot
    height = 0
    for x in range(numSliders):
        height = (x + 3) * 0.03
    height += 0.1
    
    gradeData = plt.axes([0.1, height, 0.8, 0.95 - height])
    
    plt.xlim(0, 100)
    plt.ylim(mainData.current, mainData.getHighest())
    plt.yticks(theGraph.cutOff, theGraph.letter, rotation = 0)

    x = np.linspace(0, 1000, 500)
    y = np.linspace(-1000, 1000, 500)

    global gradePlotX, gradePlotY   #global variables necessary for graph update (extends scope to update function)
    
    gradePlotX, = plt.plot(x, y, 'r')
    gradePlotY, = plt.plot(x, y, 'r')

    theGraph.setGraphInfo(numSliders, mainData.current)    #set corresponding information
    
    for x in range(numSliders):
        plotHeight = (x + 3) * 0.03
        sliderX = plt.axes([0.1, plotHeight, 0.8, 0.02])
        theSlider = Slider(sliderX,
                              theGraph.category[x].name,
                              0,
                              100,
                              0, color = 'green'
                            )
        sliders.append(theSlider)
        theGraph.addSlider(theSlider, theGraph.category[x].getInfluence())
                              
    plt.axes(gradeData)
    plt.ylabel('Final Grade')
    plt.xlabel('Overall percentage on remaining (ungraded) course categories')
    plt.title(course.name.upper())

    for x in range(numSliders):
        sliders[x].on_changed(theGraph.updateGraph)  #live update
        
    plt.show()                    

#***********************************MAIN CALCULATOR FUNCTION***********************************
#Description: Calculates and prints information corresponding to the main data (whole course).
#**********************************************************************************************

def mainDataCalculator(data, course):
    print("\n\n", course.name.upper(), " GRADE ANALYSIS", sep = '')
    print("****************************************************************************")
    print("Current Earnings:", '%.2f'%data.current, "%")
    print("Percent you had the opportunity to earn:", '%.2f'%data.possible, "%")
    print("Percent permanently lost: ", '%.2f'%data.loss, ' %', sep = '')
    print("Current Progress and Percentage is:", '%.2f'%data.progress, "%")

    if(100 - data.possible > 0.00001):
        print("Highest possible final percent (if you get 100% on rest of course work):",'%.2f'%data.getHighest(), "%")
        print("****************************************************************************")
        #Only runs if everything is not completely graded yet
        print("CUT OFFS")
        print("% Amount required (on rest of course work): \t To earn the following grade:")
        for x in range(len(course.gradeScale)):
            cutOff = float(course.gradeScale[x].cutOff)
            cutOff -= float(data.current)
            cutOff *= 100 / (100 - data.possible)
            print('',
                  format(cutOff,'20,.2f'),
                  "%\t\t\t\t\t", course.gradeScale[x].letter.strip())       
        print("****************************************************************************")
        
    else:
        print("COURSE COMPLETE ✓")
        print("****************************************************************************")

#***********************************DATA CALCULATOR FUNCTION***********************************
#Description: Calculates and prints information corresponding to each category. Accumulates
#information for the main data and stores it into object. Returns the object
#**********************************************************************************************
        
def dataCalculator(course):
    currentEarnings = 0
    percentPossible = 0
    percentLoss = 0
    finalPercent = 0
    
    print("-----------------------------------------------------")
    for x in range(course.numCategories):
        name = course.categoryByIndex(x).name
        numDone = course.categoryByIndex(x).getNumCompleted()
        numTotal = course.categoryByIndex(x).numAssessments
        maxPts = course.categoryByIndex(x).maxPtsEach
        weight = course.categoryByIndex(x).weighting
        currentStand = course.categoryByIndex(x).getPtsEarnt()
        
        maxCurrent = numDone * maxPts
        permLoss = maxCurrent - currentStand
        finalMax = numTotal * maxPts

        earned = currentStand * weight / finalMax
        possEarned = numDone * weight / numTotal
        permanentLoss = permLoss * weight / finalMax

        
        
        print(name.upper(), end = '')
        if(numDone == numTotal):
            print("| COMPLETED ✓", end = '')
            course.categoryByIndex(x).setCompletion(True)
        print("\n==================", sep = '')
        print(name + " total completed: " + str(numDone) + " / " + str(numTotal))
        if(maxCurrent == 0):
            print("Current Standing: Not Available")
        else:
            print("Curent Standing:",'%.2f'%currentStand, "/", '%.2f'%maxCurrent, end = "")
            currPercent = currentStand / maxCurrent * 100
            print(" = ", '%.2f'%currPercent, "%")
        print("Permanent Loss:",'%.2f'%permLoss)
        print("Final Standing:",'%.2f'%currentStand, "/", '%.2f\n'%finalMax)

        print(name, "| Total Percentage Weighting: ", '%.1f'%weight, " %", sep = '')
        print("Secured percentage: ", '%.2f'%earned, ' %', sep = '')
        print("Percent you had the opportunity to earn:", '%.2f'%possEarned, "%")
        print("Permanent Loss:", '%.2f'%permanentLoss, "%")
        print("-----------------------------------------------------")  

        currentEarnings += earned
        percentPossible += possEarned
        percentLoss += permanentLoss
        finalPercent += weight

    if(percentPossible != 0):
        currentProgress = currentEarnings * 100 / percentPossible
    else:
        currentProgress = 0
    
    data = mainData(currentEarnings, percentPossible, percentLoss, finalPercent, currentProgress)
    return data

#***********************************READFILE FUNCTION***********************************
#Description: Reads file containing data and validates that the file exists. Returns
#the file as a string of data.
#***************************************************************************************

def readFile():
    while(True):
        try:
            fileName = input("Enter file name to read: ")
            with open(fileName, 'r') as text:
                data = text.read()
            return data
        
        except FileNotFoundError:
            print(fileName + " does not exist.")
            print("Please also remember to add .txt to the end")
            print("And ensure the file is in the same directory as the program\n")

#***********************************INTERPRET DATA FUNCTION***********************************
#Description: interprets and validates data coming from file. Creates objects corresponding
#to course/ grades and stores information among them. Returns False if invalid data is detected.
#Returns the course object otherwise.
#*********************************************************************************************
            
def interpretData(info):
    #Course name
    courseName = finder(info, '"', 0, 1)
    if(courseName.isspace() or courseName == ''):
        print("Empty name header detected!")
        return False
    
    #number of categories
    try:
        quantity = int(finder(info, '"', 4, 5))
        if(info.count('"') != (quantity * 10 + 6)):
            print("Check the number of quotation marks")
            return False
    except:
        print("Check number of grading categories")
        return False

    #Grading scale
    gradingScale = finder(info, '"', 2, 3)
    gradingScale = gradingScale.split(',')
    updatedGradeScale = []
    for x in range(len(gradingScale)):
        updatedGradeScale.append(gradingScale[x].split(':'))

    course = Course(courseName, quantity)   #create course object
    
    for x in range(len(updatedGradeScale)):
        try:
            cutOff = float(updatedGradeScale[x][1])
            if(cutOff < 0 or cutOff > 100):
                print("Check grading scale cut off range values")
                return False
        except:
            print("Check your grading scale")
            return False
        theGrade = Grade(updatedGradeScale[x][0], cutOff)   #creates grade object
        course.addGrade(theGrade)   #adds grade object into course's grade list
        
    n = 5    #index to find strings
     
    #category information
    for x in range(quantity):  
        name = finder(info, '"', n + 1, n + 2)
        if(name.isspace() or name == ''):
            print("Empty name header detected!")
            return False  
        try:
            weighting = float(finder(info, '"', n + 3, n + 4))
            numWork = int(finder(info, '"', n + 5, n + 6))       
            maxPts = float(finder(info, '"', n + 7, n + 8))
        except:
            return False

        category = Category(name, weighting, numWork, maxPts)   #creates category object
    
        theScores = finder(info, '"', n + 9, n + 10)
        scores = theScores.split(",")
        
        if(len(scores) > numWork):
            print("There may be too many scores input in a category")
            return False
        
        if(len(scores) > 1):
            for x in range(len(scores)):
                try:
                    if(float(scores[x]) > maxPts or float(scores[x]) < 0):
                       print("Check your individual score range values")
                       return False
                    category.addScore(float(scores[x]))
                except:
                    return False
        elif(scores[0].isdigit() and len(scores) == 1):
            #there is just 1 score
            if(float(scores[0]) > maxPts or float(scores[0]) < 0):
                print("Check your individual score range values")
                return False
            category.addScore(float(scores[0]))
            
        elif((not scores[0].isspace() and scores[0] != '')):
            print("Check your individual score values")
            return False

        course.addCategory(category)    #adds category to the course's category list
        
        n += 10

    return course

#***********************************FINDER FUNCTION***********************************
#Description: Finds a string in between the keyword. nth and nth2 provide the index
#location of the starting and ending keyword. string is the data as a string passed
#as an argument to the function. Returns the string found
#*************************************************************************************

def finder(string, keyword, nth, nth2):
    substring = string.split(keyword, nth + 1)
    if len(substring) <= nth + 1:
        return -1
    indexA = len(string) - len(substring[-1]) - len(keyword)
    substring = string.split(keyword, nth2 + 1)
    if len(substring) <= nth2 + 1:
        return -1
    indexB = len(string) - len(substring[-1]) - len(keyword)
    return (string[indexA + 1:indexB])

main()
