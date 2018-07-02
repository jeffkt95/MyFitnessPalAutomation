import calendar
from enum import Enum

class MyFitnessPalGrade(Enum):
    BAD = 1
    OK = 2
    GOOD = 3
    EXCELLENT = 4

#This class rates your day Excellent, Good, OK, or Bad
class MyFitnessPalMetrics:
    #Going over by this many calories is considered "just ok"
    OK_NET_CALORIE_OVERAGE = 500

    #At least this many calories should be logged to consider the day a logging success.
    #In other words, if you don't log at least this many calories, then we doubt you logged diligently.
    MINIMUM_CALORIES_LOGGED = 600
    
    #It's considered "just ok" to go over your sugar goal by this factor
    OK_SUGAR_OVERAGE_FACTOR = 1.50
    
    #It's considered excellent to exercise at least this number of calories
    MIN_CALORIES_EXERCISED = 150

    #This table illustrates what it takes to achieve different grades
    #Metric             Excellent       Good            OK              Bad
    #Net calories       <= goal         <= goal         <= goal + 500   > goal + 500
    #Calories eaten     >= 600          >= 600          >= 600          < 600
    #Sugar consumed     <= goal         <= goal         <= goal * 1.5   > goal * 1.5
    #Exercise           >= 150 burned   < 150 burned    < 150 burned    < 150 burned
    
    def __init__(self, mfpClient, date, username):
        self.mfpClient = mfpClient
        self.date = date
        self.username = username
        self.setMetricValues()
        self.calculateGrade()
        self.dateStr = calendar.day_name[date.weekday()] + ", " + calendar.month_name[date.month] + " " + str(int(date.day))
        
    def setMetricValues(self):
        year = self.date.year
        month = self.date.month
        date = self.date.day
        
        foodDiary = self.mfpClient.get_date(year, month, date)
        exercises = self.mfpClient.get_exercise(year, month, date)
        cardio = exercises[0].get_as_list()
        #exercises[1] is strength training, which has no effect on calories. So ignore it.
        
        totals = foodDiary.totals
        goals = foodDiary.goals
        
        #iterate through all exercise entries in cardio and add up the calories burned
        self.caloriesBurned = 0
        for exercise in cardio:
            nutritionInfo = exercise['nutrition_information']
            self.caloriesBurned = self.caloriesBurned + nutritionInfo['calories burned']
        
        self.calorieGoal = goals['calories'] - self.caloriesBurned
        if 'calories' in totals:
            self.caloriesConsumed = totals['calories']
        else:
            self.caloriesConsumed = 0
        self.netCalories = self.caloriesConsumed - self.caloriesBurned
        self.sugarGoal = goals['sugar']
        if 'sugar' in totals:
            self.sugarConsumed = totals['sugar']
        else:
            self.sugarConsumed = 0
            
        metadata = self.mfpClient.user_metadata
        userprofile = metadata['profiles']
        
        self.sex = userprofile[0]['sex']
        #create capitalized and lowercase regular and possessive pronouns
        if (self.sex == "M"):
            self.proC = "He"
            self.proL = "he"
            self.proPosC = "His"
            self.proPosL = "his"
        else:
            self.proC = "She"
            self.proL = "she"
            self.proPosC = "Her"
            self.proPosL = "her"
    
    def printMetrics(self):
        print("For date: " + str(self.date))
        print("calorieGoal: " + str(self.calorieGoal))
        print("netCalories: " + str(self.netCalories))
        print("caloriesConsumed: " + str(self.caloriesConsumed))
        print("sugarGoal: " + str(self.sugarGoal))
        print("sugarConsumed: " + str(self.sugarConsumed))
        print("caloriesBurned: " + str(self.caloriesBurned))

    def calculateGrade(self):
        metNetCaloriesMetric = (self.netCalories <= self.calorieGoal)
        metCalorieMaintenanceMetric = (self.netCalories <= self.calorieGoal + self.OK_NET_CALORIE_OVERAGE)
        metMinimumLoggingGoal = (self.caloriesConsumed >= self.MINIMUM_CALORIES_LOGGED)
        metSugarConsumedGoal = (self.sugarConsumed <= self.sugarGoal)
        metSugarOverageGoal = (self.sugarConsumed <= self.sugarGoal * self.OK_SUGAR_OVERAGE_FACTOR)
        metExerciseGoal = (self.caloriesBurned >= self.MIN_CALORIES_EXERCISED)
        
        self.metNetCaloriesMetric = metNetCaloriesMetric
        self.metCalorieMaintenanceMetric = metCalorieMaintenanceMetric
        self.metMinimumLoggingGoal = metMinimumLoggingGoal
        self.metSugarConsumedGoal = metSugarConsumedGoal
        self.metSugarOverageGoal = metSugarOverageGoal
        self.metExerciseGoal = metExerciseGoal

        if (metNetCaloriesMetric and metMinimumLoggingGoal and metSugarConsumedGoal and metExerciseGoal):
            self.grade = MyFitnessPalGrade.EXCELLENT
        elif (metNetCaloriesMetric and metMinimumLoggingGoal and metSugarConsumedGoal):
            self.grade = MyFitnessPalGrade.GOOD
        elif (metCalorieMaintenanceMetric and metMinimumLoggingGoal and metSugarOverageGoal):
            self.grade = MyFitnessPalGrade.OK
        else:
            self.grade = MyFitnessPalGrade.BAD
        
        return self.grade
            
    def getGradeMessage(self):
        message = "MyFitnessPal status message for " + str(self.dateStr) + "..."
        
        calorieMessage = "Calories: net " + str(self.netCalories) + ". Goal is to stay under " + str(self.calorieGoal)
        sugarMessage = "Sugar: " + str(self.sugarConsumed) + " consumed. Goal is to stay under " + str(self.sugarGoal)
        exerciseMessage = "Exercise: " + str(self.caloriesBurned) + " calories burned exercising. Burn " + str(self.MIN_CALORIES_EXERCISED) + " to help earn an 'Excellent'."
        if (self.grade == MyFitnessPalGrade.EXCELLENT):
            message = message + "\n" + ";) Excellent!"
            message = message + "\n" + "  " + self.username + " did very well."
            message = (message + "\n" + "  " + self.username + " stayed within " + self.proPosL + " calorie goal, stayed within " + self.proPosL + 
                " sugar goal, and " + self.proL + " also exercised.")
            message = message + "\n" + "  " + "Keep it up!"
        elif (self.grade == MyFitnessPalGrade.GOOD):
            message = message + "\n" + ":) Good!"
            message = message + "\n" + "  " + self.username + " did very well."
            message = message + "\n" + "  " + self.username + " stayed within " + self.proPosL + " calorie goal and stayed within " + self.proPosL + " sugar goal."
            message = message + "\n" + "  " + "Keep it up!"
            message = message + "\n" + "  " + "To earn an 'Excellent' add " + str(self.MIN_CALORIES_EXERCISED) + " calories of exercise."
        elif (self.grade == MyFitnessPalGrade.OK):
            message = message + "\n" + ":| OK"
            message = message + "\n" + "  " + self.username + " did OK."
            message = (message + "\n" + "  " + self.username + " logged " + self.proPosL + 
                " calories, stayed at least within the maintenance calorie range, and stayed within " 
                + str(self.OK_SUGAR_OVERAGE_FACTOR) + " times the sugar goal.")
            message = message + "\n" + "  " + "To earn a good, " + self.proL + " must stay within " + self.proPosL + " calorie and sugar goals."
        elif (self.grade == MyFitnessPalGrade.BAD):
            message = message + "\n" + ":( Bad"
            message = message + "\n" + "  " + self.username + " did badly."
            if (not self.metMinimumLoggingGoal):
                message = (message + "\n" + "  " + self.username + " didn't log that day. " + self.proC + " has to log at least " + 
                    str(self.MINIMUM_CALORIES_LOGGED) + ". " + self.proC + " only logged " + str(self.netCalories) + ".")
            if (not self.metCalorieMaintenanceMetric):
                message = (message + "\n" + "  " + self.username + " exceeded his calorie goal of " + self.calorieGoal + ". " + self.proC + 
                    " netted " + self.netCalories + " calories.")
            if (not self.metSugarOverageGoal):
                message = (message + "\n" + "  " + self.username + " significantly exceeded sugar of " + self.sugarGoal + ". " + self.proC + 
                    " consumed " + self.sugarConsumed + " sugar.")
            message = message + "\n" + "  " + "To earn a good, " + self.proL + " must stay within " + self.proPosL + " calorie and sugar goals."
        
        message = message + "\n" + "  " + calorieMessage
        message = message + "\n" + "  " + sugarMessage
        message = message + "\n" + "  " + exerciseMessage
        
        return message