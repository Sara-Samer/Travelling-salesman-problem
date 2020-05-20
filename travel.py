import math
import enum
import copy


class Node:
    def __init__(self, city, timeCost=0, hueristicCost=0, visited=[], flight = None, day = None):
        self.city = city
        self.t = timeCost
        self.h = hueristicCost
        self.visited = visited
        self.flight = flight
        self.day = day
        self.totalCost = timeCost+hueristicCost

    def getVisited(self):
        return self.visited

    def getCity(self):
        return self.city

    def getTimeCost(self):
        return self.t

    def __eq__(self, other):
        sameFlight = False
        if not self.flight or not other.flight:
            sameFlight = True
        elif self.flight == other.flight:
            sameFlight = True

        return self.city == other.city and sameFlight

    def __lt__(self, other):
        if self.totalCost == other.totalCost:
            return self.city < other.city
        return self.totalCost < other.totalCost

    def __repr__(self):
        path = str([]) if (self.visited == None) else str(self.visited)
        return (" cost is: " + str(self.totalCost) + "\n" + path)

class Day:
    def __init__(self, day, time):
        self.day = day
        self.time = time
    def __repr__(self):
        return str(self.day) + " " + str(self.time)
    
    def __sub__(self, other):
        minutes = self.time - other.time if self.time >= other.time else other.time - self.time
        hours = (self.day.value - other.day.value)*24*60
        total = 0
        if(self.day == other.day):
            total = minutes
        elif(self.time > other.time):
            total = hours + minutes
        else:
            total = hours - minutes
    
        return total
        
    def add(self, minutes):
        time = Time(minutes=minutes) + self.time
        daysToAdd = 0
        if(time.minutes >= 60):
            time.hours += int(time.minutes/60)
            time.minutes = time.minutes%60
        if(time.hours >= 24):
            daysToAdd = int(time.hours/24)
            time.hours = time.hours%24
        day = daysToAdd + self.day.value
        if day <= 7:
            self.day = WeekDays(day)
            self.time = time
            
    def __eq__(self, other):
        return self.day == other.day and self.time == other.time
    def __gt__(self, other):
        if(self.day.value > other.day.value):
            return True
        elif(self.day.value == other.day.value) and (self.time > other.time):
            return True
        else:
            return False        
        
class Time:
    def __init__(self, hours=0, minutes=0):
        h = hours
        m = minutes
        if(minutes >= 60 and h == 0):
            h = int(minutes/60)
            m = minutes % 60
        self.hours = h
        self.minutes = m

    def __eq__(self, other):
        return self.hours == other.hours and self.minutes == other.minutes

    def __lt__(self, other):
        if(self.hours < other.hours):
            return True
        elif(self.hours == other.hours):
            return self.minutes < other.minutes
        else:
            return False

    def __ge__(self, other):
        if(self.hours > other.hours):
            return True
        elif(self.hours == other.hours):
            return self.minutes >= other.minutes
        else:
            return False

    def __add__(self, other):
        h = self.hours + other.hours
        m = self.minutes + other.minutes
        if(m >= 60):
            m %= 60
            h += 1
        return Time(h, m)

    def __sub__(self, other):
        h = self.hours - other.hours
        m = self.minutes - other.minutes
        if(h < 0):
            h += 24
        if(m < 0):
            m += 60
            h -= 1
        return h*60+m

    def __repr__(self):
        h = (str(self.hours) if self.hours > 9 else"0" + str(self.hours))
        m = (str(self.minutes) if self.minutes > 9 else"0" + str(self.minutes))
        return h + ":" + m

    def add(self, mins):
        t = Time(minutes=mins)
        return self + t

class City:
    def __init__(self, city, x, y):
        self.city = city
        self.x = x
        self.y = y

    def getDistanceFrom(self, other):
        x = (self.x - other.x)**2
        y = (self.y - other.y)**2
        return (x+y)**(1/2)

    def getName(self):
        return self.city

    def __repr__(self):
        return (self.city)
    
    def __lt__(self, other):
        return self.city < other.city
    
    def __eq__(self, other):
        return self.city == other.city

class Flight:
    def __init__(self, sourceCity, destinationCity, departureTime, arrivalTime, name, days):
        self.sourceCity = sourceCity
        self.destinationCity = destinationCity
        self.departureTime = departureTime
        self.arrivalTime = arrivalTime
        self.name = name
        self.days = days

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return ("from: " + str(self.sourceCity) + " To: " + str(self.destinationCity) + " name: " + self.name + " departure time: " + str(self.departureTime) + " and arrival time: " + str(self.arrivalTime))
        # return ("name:" + self.name+" duration is:" + str(self.getDuration()))

    def getDays(self):
        return self.days

    def getDuration(self):
        return self.arrivalTime - self.departureTime

    def getSourceCity(self):
        return self.sourceCity

    def getDestinationCity(self):
        return self.destinationCity

class TimeTable:
    def __init__(self, cityFrom, cityTo, flights):
        self.cityFrom = cityFrom
        self.cityTo = cityTo
        self.flights = flights

    def getCityFrom(self):
        return self.cityFrom

    def getCityTo(self):
        return self.cityTo

    def getFlights(self):
        return self.flights

    def __repr__(self):
        return ("from" + str(self.cityFrom) + " to" + str(self.cityTo) + " flights:" + str(self.flights))

def getFlights(names, flights):
    return [flight for flight in flights if flight.name in names]

def getAvailableCities(city, flights):
    return [flight for flight in flights if city == flight.getSourceCity()]

def addToOpen(_next, _open):
    for node in _open:
        # is same city and hueristic is less then add to open
        c1 = int(_next.totalCost)
        c2 = int(node.totalCost)
        if (_next == node and c1 >= c2):
            return False
    return True

def alreadyInClosed(_next, closed):
    for node in closed:
        f1 = _next.flight
        f2 = node.flight
        if(not f1 or not f2):
            continue
        if ( f1.destinationCity == f2.sourceCity and _next.totalCost >= node.totalCost):
            return True
    return False

def travel(start, goal, startDay, endDay, flights):
    # inialize posible paths list
    paths = []
    fullDay = Time(23, 59)
    for d in range(startDay.value, endDay.value + 1):
        # Initialize open and closed lists
        _open = []
        closed = []
        
        # Initialize start time 00:00
        # This variable is made to keep track of the time in the search
        # time = Time()

        # Get day enum
        # day = WeekDays(d)
        
        # initialize day object
        initialDayTime = Day(WeekDays(d), Time())

        # Set Start and goal nodes
        startNode = Node(start, day=initialDayTime)
        goalNode = Node(goal)
    
        # Add start node to open list
        _open.append(startNode)
        while len(_open) > 0:

            # Open list will be sorted by total cost ascending
            _open.sort()

            # Get first node (one with least cost) and set as current
            currentNode = _open.pop(0)
            currentCity = currentNode.getCity()
            currentDayTime = currentNode.day
            
            # # If a full day has passed then Increase the 'day' and recalculate time
            # if(time >= fullDay):
            #     nextDay = d + 1
            #     if(nextDay >= 8):
            #         break
            #     day = WeekDays(nextDay)
            #     time = Time(minutes=(time - fullDay))

            # Add current node as visited
            closed.append(currentNode)

            # If it's the goal add to possible paths then break out of the loop
            if currentNode == goalNode:
                paths.append(currentNode)
                break
            # If not then get children of current node
            children = getAvailableCities(currentCity, flights)

            # And for each child calculate hueristic and cost then append to open list

            # This loop iterates only on flights that are available in current day
            for flight in children:
        # # This loop iterates on each day from current to end to get available flights in these days
                 # for takeOff in range(currentDayTime.day.value, endDay.value+1):
            
                # For each flight make sure it takes off in current day
                if currentDayTime.day not in flight.getDays():
                    continue
                
                if currentDayTime.time > flight.departureTime:
                    continue
                
                #initialize a day with the flight day and departure time
                flightDay = Day(WeekDays(currentDayTime.day), flight.departureTime)
                nextDay = copy.deepcopy(currentDayTime)
                
                
                # Calculate passed days 
                # First calculate waiting time
                # which is time from now to flight departure
                waitingTime = (flightDay - currentDayTime)
                
                if(currentNode == startNode):
                    waitingTime = 0    
                
                # Get Destination of the flight
                nextCity = flight.getDestinationCity()
                
                # calculate hueristic from distance
                hueristic = currentCity.getDistanceFrom(nextCity)
                
                # calculate flight cost
                # cost is flight duration + waiting time
                duration = flight.getDuration()
                
                temp = copy.deepcopy(nextDay)
                nextDay.add((flightDay - currentDayTime) + duration)
                
                if(temp == nextDay):
                    continue
                # Keeping track of the path
                visited = list(currentNode.visited)
                visited.append("from Day: " + str(currentDayTime) + " To Day: " + str(nextDay) +" h: " + str(hueristic)  + " --> " + str(flight) + "\n")
                node = Node(nextCity, currentNode.t + waitingTime, hueristic, visited, flight, nextDay)

                # If it's already visited then don't add and search for others
                if alreadyInClosed(node, closed):
                    continue

                # if addToOpen(node, _open):
                if addToOpen(node, list(_open + paths)):
                    _open.append(node)
                    
                # # For each flight of make it takes of in current day
                # if day not in flight.getDays():
                #     continue

                # nextCity = flight.getDestinationCity()
                # # calculate hueristic from distance
                # hueristic = currentCity.getDistanceFrom(nextCity)

                # # calculate flight cost
                # # if it's the first time don't calculate waiting time
                # if(currentNode == startNode):
                #     cost = flight.getDuration()
                #     time = flight.arrivalTime # + cost
                # else:
                #     # First calculate waiting time
                #     # which is  time since arrival of last flight - departure of current flight
                #     # cost is flight duration + waiting time
                #     # and the time is increased by the flight duration and waiting time
                #     waitingTime = time - flight.departureTime
                #     cost = flight.getDuration() + waitingTime
                #     time = time.add(flight.getDuration() + waitingTime)

                # # Keeping track of the path
                # visited = list(currentNode.visited)
                # visited.append(flight)
                
                # node = Node(nextCity, cost, hueristic, visited)

                # # If it's already visited then don't add and search for others
                # if alreadyInClosed(node, closed):
                #     continue

                # # if addToOpen(node, _open):
                # if addToOpen(node, list(_open + paths)):
                #     _open.append(node)
    paths.sort()
    return paths

class WeekDays(enum.Enum):
    sat = 1
    sun = 2
    mon = 3
    tue = 4
    wed = 5
    thu = 6
    fri = 7

def main():
    cities = loadCities()
    flights = loadFlights(cities)
    source = cities["Cairo"]
    destination = cities["New York"]
    t1 = Time(11,00)
    t2 = Time(12,00)
    # t2 = Time(minutes=3270)
    # print(t2)
    d1 = Day(WeekDays.mon, t1)
    d2 = Day(WeekDays.mon, t2)
    print(d1 - d2)
    # while True:
    #     try:
    #         source = cities[input("Enter start city:")]
    #         destination = cities[input("Enter destination city:")]
    #         print("WeekDays: sat, sun, mon, tue, wed, thu and fri")
    #         startDay = WeekDays[input("Enter start day:")]
    #         endDay = WeekDays[input("Enter end day:")]
    #     except:
    #         print("Invalid input please try again")
    #     else:
    #         break
    paths = travel(source, destination, WeekDays.sat, WeekDays.fri, flights)

    # paths = travel(source, destination, WeekDays.sun, WeekDays.mon, flights)
    i = 1
    for path in paths:
        print("-------------- Path option: " + str(i) + " -----------------")
        i += 1
        print("Cost = " + str(path.totalCost))
        print("Total Cost = " + str(path.totalCost))
        print(*path.visited, sep="\n")


def loadCities():
    cities = {}
    cities["Alexandria"] = City("Alexandria", 31.2, 29.95)
    cities["Aswan"] = City("Aswan", 24.0875, 32.8989)
    cities["Cairo"] = City("Cairo", 30.05, 31.25)
    cities["Chicago"] = City("Chicago", 41.8373, -87.6862)
    cities["Edinburgh"] = City("Edinburgh", 55.9483, -3.2191)
    cities["Liverpool"] = City("Liverpool", 53.416, -2.918)
    cities["London"] = City("London", 51.5, -0.1167)
    cities["Lyon"] = City("Lyon", 45.77, 4.83)
    cities["Manchester"] = City("Manchester", 53.5004, -2.248)
    cities["Miami"] = City("Miami", 25.7839, -80.2102)
    cities["Milan"] = City("Milan", 45.47, 9.205)
    cities["New York"] = City("New York", 40.6943, -73.9249)
    cities["Nice"] = City("Nice", 43.715, 7.265)
    cities["Paris"] = City("Paris", 48.8667, 2.3333)
    cities["Port Said"] = City("Port Said", 31.26, 32.29)
    cities["Rome"] = City("Rome", 41.896, 12.4833)
    cities["San Francisco"] = City("San Francisco", 37.7562, -122.443)
    cities["Shanghai"] = City("Shanghai", 31.2165, 121.4365)
    cities["Tokyo"] = City("Tokyo", 35.685, 139.7514)
    cities["Venice"] = City("Venice", 45.4387, 12.335)
    return cities


def loadFlights(cities):
    flights = []
    flights.append(Flight(cities["Alexandria"], cities["Aswan"], Time(
        11, 00), Time(12, 15), "MS005", [WeekDays.mon, WeekDays.tue, WeekDays.wed]))
    flights.append(Flight(cities["Alexandria"], cities["Aswan"], Time(
        15, 15), Time(16, 30), "MS004", [WeekDays.sat, WeekDays.fri]))
    flights.append(Flight(cities["Alexandria"], cities["Cairo"], Time(
        9, 15), Time(10, 00), "MS003", [WeekDays.mon, WeekDays.tue, WeekDays.wed]))
    flights.append(Flight(cities["Alexandria"], cities["Cairo"], Time(
        12, 30), Time(13, 15), "MS001", [WeekDays.sat, WeekDays.sun]))
    flights.append(Flight(cities["Alexandria"], cities["Cairo"], Time(
        17, 00), Time(17, 45), "MS002", [WeekDays.sat, WeekDays.mon, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Alexandria"], cities["London"], Time(
        19, 30), Time(0, 32), "MS006", [WeekDays.sat, WeekDays.sun, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Alexandria"], cities["New York"], Time(
        2, 00), Time(15, 14), "MS007", [WeekDays.sun, WeekDays.tue, WeekDays.thu]))
    flights.append(Flight(cities["Aswan"], cities["Cairo"], Time(10, 20), Time(
        11, 40), "MS022", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.wed]))
    flights.append(Flight(cities["Aswan"], cities["Port Said"], Time(
        7, 5), Time(8, 18), "MS023", [WeekDays.tue, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Cairo"], cities["Alexandria"], Time(
        13, 00), Time(13, 45), "MS008", [WeekDays.sun, WeekDays.mon, WeekDays.wed]))
    flights.append(Flight(cities["Cairo"], cities["Alexandria"], Time(
        20, 15), Time(21, 00), "MS009", [WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Cairo"], cities["Aswan"], Time(
        8, 00), Time(9, 20), "MS010", [WeekDays.sun, WeekDays.wed]))
    flights.append(Flight(cities["Cairo"], cities["Aswan"], Time(
        17, 15), Time(18, 35), "MS011", [WeekDays.sat, WeekDays.tue, WeekDays.thu]))
    flights.append(Flight(cities["Cairo"], cities["London"], Time(
        10, 00), Time(15, 10), "MS014", [WeekDays.sun, WeekDays.mon, WeekDays.tue]))
    flights.append(Flight(cities["Cairo"], cities["London"], Time(
        15, 15), Time(20, 25), "MS015", [WeekDays.sat, WeekDays.wed, WeekDays.thu]))
    flights.append(Flight(cities["Cairo"], cities["New York"], Time(
        3, 00), Time(15, 5), "MS016", [WeekDays.sat, WeekDays.sun, WeekDays.wed]))
    flights.append(Flight(cities["Cairo"], cities["New York"], Time(
        19, 30), Time(7, 35), "MS017", [WeekDays.mon, WeekDays.tue, WeekDays.fri]))
    flights.append(Flight(cities["Cairo"], cities["Paris"], Time(
        2, 00), Time(6, 55), "MS018", [WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Cairo"], cities["Paris"], Time(
        5, 00), Time(9, 55), "MS019", [WeekDays.sat, WeekDays.mon]))
    flights.append(Flight(cities["Cairo"], cities["Port Said"], Time(
        11, 00), Time(11, 20), "MS013", [WeekDays.mon]))
    flights.append(Flight(cities["Cairo"], cities["Port Said"], Time(
        19, 30), Time(19, 50), "MS012", [WeekDays.sat, WeekDays.sun, WeekDays.wed, WeekDays.thu]))
    flights.append(Flight(cities["Cairo"], cities["Rome"], Time(6, 00), Time(
        9, 30), "MS021", [WeekDays.sat, WeekDays.sun, WeekDays.tue, WeekDays.thu]))
    flights.append(Flight(cities["Cairo"], cities["Shanghai"], Time(
        5, 30), Time(19, 00), "MS020", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.wed]))
    flights.append(Flight(cities["Chicago"], cities["London"], Time(
        8, 00), Time(18, 32), "DL050", [WeekDays.sun, WeekDays.tue, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Chicago"], cities["London"], Time(
        12, 10), Time(22, 42), "DL051", [WeekDays.sat, WeekDays.mon, WeekDays.wed]))
    flights.append(Flight(cities["Chicago"], cities["Miami"], Time(10, 00), Time(
        14, 20), "DL046", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.fri]))
    flights.append(Flight(cities["Chicago"], cities["Miami"], Time(
        17, 20), Time(21, 40), "DL047", [WeekDays.sun, WeekDays.tue]))
    flights.append(Flight(cities["Chicago"], cities["New York"], Time(
        9, 00), Time(11, 18), "DL044", [WeekDays.sat, WeekDays.mon, WeekDays.wed, WeekDays.fri]))
    flights.append(Flight(cities["Chicago"], cities["New York"], Time(
        15, 00), Time(17, 18), "DL045", [WeekDays.sun, WeekDays.tue]))
    flights.append(Flight(cities["Chicago"], cities["Paris"], Time(5, 00), Time(
        16, 55), "DL052", [WeekDays.sat, WeekDays.sun, WeekDays.tue, WeekDays.thu]))
    flights.append(Flight(cities["Chicago"], cities["San Francisco"], Time(
        16, 00), Time(22, 10), "DL048", [WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Chicago"], cities["San Francisco"], Time(
        20, 00), Time(2, 10), "DL049", [WeekDays.sun, WeekDays.mon, WeekDays.tue]))
    flights.append(Flight(cities["Edinburgh"], cities["London"], Time(7, 00), Time(
        8, 15), "BA128", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Edinburgh"], cities["London"], Time(19, 15), Time(
        20, 30), "BA129", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Edinburgh"], cities["Paris"], Time(14, 00), Time(
        15, 50), "BA130", [WeekDays.sat, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.fri]))
    flights.append(Flight(cities["Edinburgh"], cities["San Francisco"], Time(
        3, 00), Time(15, 10), "BA131", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.thu]))
    flights.append(Flight(cities["Liverpool"], cities["London"], Time(
        4, 30), Time(5, 30), "BA125", [WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Liverpool"], cities["London"], Time(10, 00), Time(
        11, 00), "BA123", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Liverpool"], cities["London"], Time(
        16, 00), Time(17, 00), "BA124", [WeekDays.sat, WeekDays.sun, WeekDays.mon]))
    flights.append(Flight(cities["London"], cities["Alexandria"], Time(
        6, 00), Time(11, 20), "BA149", [WeekDays.sun, WeekDays.mon, WeekDays.wed]))
    flights.append(Flight(cities["London"], cities["Cairo"], Time(10, 00), Time(
        14, 40), "BA143", [WeekDays.sat, WeekDays.sun, WeekDays.tue, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["Cairo"], Time(
        20, 00), Time(0, 40), "BA144", [WeekDays.tue, WeekDays.thu]))
    flights.append(Flight(cities["London"], cities["Chicago"], Time(4, 00), Time(
        12, 50), "BA147", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["Edinburgh"], Time(5, 00), Time(
        6, 15), "BA134", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["Edinburgh"], Time(
        17, 00), Time(18, 15), "BA135", [WeekDays.sun, WeekDays.wed, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["Liverpool"], Time(8, 40), Time(
        9, 40), "BA132", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["Liverpool"], Time(
        21, 00), Time(22, 00), "BA133", [WeekDays.sun, WeekDays.mon, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["Lyon"], Time(15, 00), Time(
        16, 35), "BA150", [WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["Manchester"], Time(10, 00), Time(
        11, 00), "BA136", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["New York"], Time(5, 00), Time(
        13, 00), "BA138", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["New York"], Time(14, 00), Time(
        22, 00), "BA145", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["Paris"], Time(6, 30), Time(
        7, 40), "BA140", [WeekDays.mon, WeekDays.tue, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["Paris"], Time(16, 00), Time(
        17, 10), "BA139", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["Rome"], Time(17, 00), Time(
        19, 20), "BA141", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["San Francisco"], Time(15, 30), Time(
        2, 30), "BA146", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["Shanghai"], Time(
        4, 30), Time(15, 30), "BA142", [WeekDays.mon, WeekDays.tue, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["Shanghai"], Time(11, 00), Time(
        22, 00), "BA137", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["London"], cities["Tokyo"], Time(14, 00), Time(
        1, 40), "BA148", [WeekDays.sat, WeekDays.sun, WeekDays.wed, WeekDays.thu]))
    flights.append(Flight(cities["Lyon"], cities["Nice"], Time(2, 10), Time(3, 00), "AF122", [
                   WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Lyon"], cities["Nice"], Time(13, 30), Time(
        14, 20), "AF121", [WeekDays.sat, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Lyon"], cities["Paris"], Time(9, 00), Time(10, 5), "AF119", [
                   WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Lyon"], cities["Paris"], Time(18, 00), Time(19, 5), "AF120", [
                   WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Manchester"], cities["London"], Time(11, 30), Time(
        12, 30), "BA126", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Manchester"], cities["London"], Time(18, 30), Time(
        19, 30), "BA127", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed]))
    flights.append(Flight(cities["Miami"], cities["Chicago"], Time(
        8, 00), Time(12, 20), "DL056", [WeekDays.mon, WeekDays.wed, WeekDays.fri]))
    flights.append(Flight(cities["Miami"], cities["New York"], Time(
        10, 00), Time(12, 55), "DL053", [WeekDays.sun, WeekDays.mon, WeekDays.tue]))
    flights.append(Flight(cities["Miami"], cities["New York"], Time(
        16, 00), Time(18, 55), "DL054", [WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Miami"], cities["San Francisco"], Time(
        10, 00), Time(16, 25), "DL055", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.wed]))
    flights.append(Flight(cities["Milan"], cities["London"], Time(14, 00), Time(
        15, 50), "AZ103", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Milan"], cities["Paris"], Time(10, 00), Time(
        11, 20), "AZ101", [WeekDays.sat, WeekDays.sun, WeekDays.tue, WeekDays.wed]))
    flights.append(Flight(cities["Milan"], cities["Paris"], Time(
        16, 00), Time(17, 20), "AZ102", [WeekDays.mon, WeekDays.fri]))
    flights.append(Flight(cities["Milan"], cities["Rome"], Time(
        1, 00), Time(2, 5), "AZ104", [WeekDays.mon, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Milan"], cities["Rome"], Time(7, 00), Time(8, 5), "AZ099", [
                   WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Milan"], cities["Rome"], Time(17, 00), Time(18, 5), "AZ100", [
                   WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["New York"], cities["Chicago"], Time(
        7, 00), Time(9, 18), "DL028", [WeekDays.sat, WeekDays.mon, WeekDays.tue]))
    flights.append(Flight(cities["New York"], cities["Chicago"], Time(
        13, 20), Time(15, 38), "DL029", [WeekDays.sat, WeekDays.sun, WeekDays.thu]))
    flights.append(Flight(cities["New York"], cities["Edinburgh"], Time(
        6, 00), Time(15, 5), "DL038", [WeekDays.sun, WeekDays.wed, WeekDays.fri]))
    flights.append(Flight(cities["New York"], cities["London"], Time(
        4, 00), Time(10, 50), "DL037", [WeekDays.sat, WeekDays.mon, WeekDays.tue, WeekDays.thu]))
    flights.append(Flight(cities["New York"], cities["Lyon"], Time(
        13, 00), Time(22, 12), "DL041", [WeekDays.sat, WeekDays.mon, WeekDays.tue]))
    flights.append(Flight(cities["New York"], cities["Miami"], Time(
        1, 00), Time(3, 55), "DL036", [WeekDays.tue]))
    flights.append(Flight(cities["New York"], cities["Miami"], Time(
        7, 15), Time(10, 10), "DL035", [WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["New York"], cities["Miami"], Time(
        12, 00), Time(14, 55), "DL034", [WeekDays.sat, WeekDays.sun, WeekDays.mon]))
    flights.append(Flight(cities["New York"], cities["Paris"], Time(
        11, 00), Time(17, 50), "DL040", [WeekDays.sun, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["New York"], cities["Rome"], Time(10, 15), Time(
        18, 30), "DL039", [WeekDays.sat, WeekDays.mon, WeekDays.tue, WeekDays.thu]))
    flights.append(Flight(cities["New York"], cities["San Francisco"], Time(
        8, 00), Time(14, 32), "DL030", [WeekDays.sun, WeekDays.mon]))
    flights.append(Flight(cities["New York"], cities["San Francisco"], Time(
        10, 00), Time(16, 32), "DL031", [WeekDays.wed, WeekDays.fri]))
    flights.append(Flight(cities["New York"], cities["San Francisco"], Time(
        18, 00), Time(0, 32), "DL032", [WeekDays.thu]))
    flights.append(Flight(cities["New York"], cities["San Francisco"], Time(
        23, 30), Time(6, 2), "DL033", [WeekDays.sat, WeekDays.tue]))
    flights.append(Flight(cities["New York"], cities["Shanghai"], Time(
        5, 00), Time(19, 50), "DL043", [WeekDays.sat, WeekDays.mon, WeekDays.wed, WeekDays.fri]))
    flights.append(Flight(cities["New York"], cities["Tokyo"], Time(
        0, 00), Time(13, 45), "DL042", [WeekDays.sat, WeekDays.sun, WeekDays.tue, WeekDays.thu]))
    flights.append(Flight(cities["Nice"], cities["Lyon"], Time(20, 00), Time(20, 50), "AF118", [
                   WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Nice"], cities["Paris"], Time(5, 00), Time(6, 20), "AF117", [
                   WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Nice"], cities["Paris"], Time(
        14, 30), Time(15, 50), "AF116", [WeekDays.sat, WeekDays.sun, WeekDays.fri]))
    flights.append(Flight(cities["Paris"], cities["London"], Time(9, 00), Time(
        10, 5), "AF105", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Paris"], cities["London"], Time(22, 00), Time(
        23, 5), "AF106", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Paris"], cities["Lyon"], Time(7, 00), Time(
        8, 10), "AF114", [WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu]))
    flights.append(Flight(cities["Paris"], cities["Lyon"], Time(14, 00), Time(
        15, 10), "AF115", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Paris"], cities["New York"], Time(12, 00), Time(
        20, 30), "AF107", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Paris"], cities["New York"], Time(
        17, 30), Time(2, 00), "AF108", [WeekDays.sat, WeekDays.sun, WeekDays.fri]))
    flights.append(Flight(cities["Paris"], cities["Nice"], Time(11, 00), Time(12, 20), "AF112", [
                   WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Paris"], cities["Nice"], Time(16, 00), Time(17, 20), "AF113", [
                   WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Paris"], cities["Rome"], Time(10, 00), Time(12, 00), "AF110", [
                   WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Paris"], cities["Rome"], Time(18, 00), Time(
        20, 00), "AF109", [WeekDays.sun, WeekDays.tue, WeekDays.wed, WeekDays.fri]))
    flights.append(Flight(cities["Paris"], cities["Shanghai"], Time(
        4, 00), Time(15, 55), "AF111", [WeekDays.sat, WeekDays.mon]))
    flights.append(Flight(cities["Port Said"], cities["Alexandria"], Time(
        12, 00), Time(12, 30), "MS026", [WeekDays.sun, WeekDays.mon, WeekDays.wed]))
    flights.append(Flight(cities["Port Said"], cities["Alexandria"], Time(
        14, 45), Time(15, 15), "MS027", [WeekDays.sat, WeekDays.tue, WeekDays.thu]))
    flights.append(Flight(cities["Port Said"], cities["Cairo"], Time(
        11, 00), Time(11, 20), "MS024", [WeekDays.sat, WeekDays.mon]))
    flights.append(Flight(cities["Port Said"], cities["Cairo"], Time(
        14, 10), Time(14, 30), "MS025", [WeekDays.wed, WeekDays.fri]))
    flights.append(Flight(cities["Rome"], cities["London"], Time(1, 00), Time(3, 30), "AZ091", [
                   WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Rome"], cities["London"], Time(11, 30), Time(
        14, 00), "AZ090", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Rome"], cities["Milan"], Time(8, 00), Time(9, 5), "AZ094", [
                   WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Rome"], cities["Milan"], Time(22, 00), Time(
        23, 5), "AZ095", [WeekDays.mon, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Rome"], cities["New York"], Time(4, 00), Time(
        13, 48), "AZ088", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Rome"], cities["New York"], Time(
        17, 00), Time(2, 48), "AZ089", [WeekDays.tue, WeekDays.wed, WeekDays.fri]))
    flights.append(Flight(cities["Rome"], cities["Paris"], Time(8, 00), Time(10, 00), "AZ086", [
                   WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Rome"], cities["Paris"], Time(20, 00), Time(
        22, 00), "AZ087", [WeekDays.mon, WeekDays.tue, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Rome"], cities["Venice"], Time(11, 00), Time(
        12, 00), "AZ092", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Rome"], cities["Venice"], Time(18, 00), Time(
        19, 00), "AZ093", [WeekDays.sat, WeekDays.mon, WeekDays.wed, WeekDays.fri]))
    flights.append(Flight(cities["San Francisco"], cities["Chicago"], Time(
        7, 00), Time(13, 10), "DL059", [WeekDays.tue, WeekDays.wed, WeekDays.thu]))
    flights.append(Flight(cities["San Francisco"], cities["Chicago"], Time(
        14, 00), Time(20, 10), "DL060", [WeekDays.sat, WeekDays.sun, WeekDays.fri]))
    flights.append(Flight(cities["San Francisco"], cities["Miami"], Time(
        11, 00), Time(17, 25), "DL061", [WeekDays.sun, WeekDays.mon, WeekDays.wed, WeekDays.thu]))
    flights.append(Flight(cities["San Francisco"], cities["New York"], Time(
        6, 00), Time(12, 32), "DL057", [WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["San Francisco"], cities["New York"], Time(
        13, 00), Time(19, 32), "DL058", [WeekDays.sat, WeekDays.sun, WeekDays.mon]))
    flights.append(Flight(cities["Shanghai"], cities["Cairo"], Time(2, 00), Time(
        16, 30), "CA070", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Cairo"], Time(7, 00), Time(
        21, 30), "CA068", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Cairo"], Time(13, 30), Time(
        4, 00), "CA069", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Chicago"], Time(6, 00), Time(
        19, 45), "CA080", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Chicago"], Time(15, 00), Time(
        4, 45), "CA081", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["London"], Time(0, 40), Time(
        13, 20), "CA071", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["London"], Time(5, 30), Time(
        18, 10), "CA072", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["London"], Time(14, 00), Time(
        2, 40), "CA073", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["New York"], Time(1, 00), Time(
        15, 50), "CA079", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["New York"], Time(10, 00), Time(
        0, 50), "CA078", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Paris"], Time(2, 00), Time(
        14, 25), "CA076", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Paris"], Time(8, 00), Time(
        20, 25), "CA077", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Rome"], Time(6, 00), Time(
        19, 10), "CA074", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Rome"], Time(17, 00), Time(
        6, 10), "CA075", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Tokyo"], Time(5, 00), Time(
        7, 50), "CA085", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Tokyo"], Time(12, 00), Time(
        14, 50), "CA082", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Tokyo"], Time(16, 00), Time(
        18, 50), "CA083", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Tokyo"], Time(21, 00), Time(
        23, 50), "CA084", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Tokyo"], cities["San Francisco"], Time(12, 00), Time(
        21, 5), "JL066", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.wed, WeekDays.thu]))
    flights.append(Flight(cities["Tokyo"], cities["San Francisco"], Time(22, 00), Time(
        7, 5), "JL067", [WeekDays.sat, WeekDays.mon, WeekDays.tue, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Tokyo"], cities["Shanghai"], Time(
        0, 00), Time(2, 50), "JL063", [WeekDays.sun, WeekDays.tue, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Tokyo"], cities["Shanghai"], Time(
        6, 10), Time(9, 00), "JL064", [WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed]))
    flights.append(Flight(cities["Tokyo"], cities["Shanghai"], Time(
        9, 00), Time(11, 50), "JL065", [WeekDays.sat, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Tokyo"], cities["Shanghai"], Time(
        20, 00), Time(22, 50), "JL062", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.wed]))
    flights.append(Flight(cities["Venice"], cities["Rome"], Time(5, 00), Time(6, 00), "AZ096", [
                   WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Venice"], cities["Rome"], Time(14, 00), Time(
        15, 00), "AZ097", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    flights.append(Flight(cities["Venice"], cities["Rome"], Time(19, 40), Time(
        20, 40), "AZ098", [WeekDays.sat, WeekDays.sun, WeekDays.mon, WeekDays.tue, WeekDays.wed, WeekDays.thu, WeekDays.fri]))
    return flights


if __name__ == '__main__':
    main()
