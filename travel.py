import math
import enum


class Node:
    def __init__(self, city, timeCost=0, hueristicCost=0, visited=[]):
        self.city = city
        self.t = timeCost
        self.h = hueristicCost
        self.visited = visited
        self.totalCost = timeCost+hueristicCost

    def getVisited(self):
        return self.visited

    def getCity(self):
        return self.city

    def getTimeCost(self):
        return self.t

    def __eq__(self, other):
        return self.city == other.city

    def __lt__(self, other):
        if self.totalCost == other.totalCost:
            return self.city < other.city
        return self.totalCost < other.totalCost

    def __repr__(self):
        path = str([]) if (self.visited == None) else str(self.visited)
        return (" cost is: " + str(self.totalCost) + "\n" + path)

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
        if(self < other):
            t = self
            self = other
            other = t
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
        return (x+y)**1/2

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
        if (_next == node and _next.totalCost >= node.totalCost):
            return True
    return False


def travel(start, goal, startDay, endDay, flights):
    paths = []
    fullDay = Time(24, 59)
    for d in range(startDay.value, endDay.value + 1):
        # Initialize open and closed lists
        _open = []
        closed = []
        
        # Initialize start time 00:00
        # This variable is made to keep track of the time in the search
        time = Time()

        # Get day enum
        day = Days(d)
        # Track of flights
        track = str(start)
        
        # Set Start and goal nodes
        startNode = Node(start)
        goalNode = Node(goal)

        # Add start node to open list
        _open.append(startNode)
        while len(_open) > 0:

            # Open list will be sorted by total cost ascending
            _open.sort()

            # Get first node (one with least cost) and set as current
            currentNode = _open.pop(0)
            currentCity = currentNode.getCity()
            
            # If a full day has passed then Increase the 'day' and recalculate time
            if(time >= fullDay):
                nextDay = d + 1
                if(nextDay >= 8):
                    break
                day = Days(nextDay)
                time = Time(minutes=(time - fullDay))

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

                # For each flight of make it takes of in current day
                if day not in flight.getDays():
                    continue

                nextCity = flight.getDestinationCity()
                # calculate hueristic from distance
                hueristic = currentCity.getDistanceFrom(nextCity)

                # calculate flight cost
                # if it's the first time don't calculate waiting time
                if(currentNode == startNode):
                    cost = flight.getDuration()
                    time = flight.arrivalTime
                else:
                    # First calculate waiting time
                    # which is  time since arrival of last flight - departure of current flight
                    # cost is flight duration + waiting time
                    # and the time is increased by the flight duration and waiting time
                    waitingTime = time - flight.departureTime
                    cost = flight.getDuration() + waitingTime
                    time = time.add(flight.getDuration() + waitingTime)

                # Keeping track of the path
                visited = list(currentNode.visited)
                visited.append(flight)
                
                node = Node(nextCity, cost, hueristic, visited)

                # If it's already visited then don't add and search for others
                if alreadyInClosed(node, closed):
                    continue

                # if addToOpen(node, _open):
                if addToOpen(node, list(_open + paths)):
                    _open.append(node)
    paths.sort()
    return paths


class Days(enum.Enum):
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

    # while True:
    #     try:
    #         source = cities[input("Enter start city:")]
    #         destination = cities[input("Enter destination city:")]
    #         print("Days: sat, sun, mon, tue, wed, thu and fri")
    #         startDay = Days[input("Enter start day:")]
    #         endDay = Days[input("Enter end day:")]
    #     except:
    #         print("Invalid input please try again")
    #     else:
    #         break
    paths = travel(source, destination, Days.sat, Days.fri, flights)

    # paths = travel(source, destination, Days.sun, Days.mon, flights)
    i = 1
    for path in paths:
        print("-------------- Path option: " + str(i) + " -----------------")
        i += 1
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
        11, 00), Time(12, 15), "MS005", [Days.mon, Days.tue, Days.wed]))
    flights.append(Flight(cities["Alexandria"], cities["Aswan"], Time(
        15, 15), Time(16, 30), "MS004", [Days.sat, Days.fri]))
    flights.append(Flight(cities["Alexandria"], cities["Cairo"], Time(
        9, 15), Time(10, 00), "MS003", [Days.mon, Days.tue, Days.wed]))
    flights.append(Flight(cities["Alexandria"], cities["Cairo"], Time(
        12, 30), Time(13, 15), "MS001", [Days.sat, Days.sun]))
    flights.append(Flight(cities["Alexandria"], cities["Cairo"], Time(
        17, 00), Time(17, 45), "MS002", [Days.sat, Days.mon, Days.thu, Days.fri]))
    flights.append(Flight(cities["Alexandria"], cities["London"], Time(
        19, 30), Time(0, 32), "MS006", [Days.sat, Days.sun, Days.thu, Days.fri]))
    flights.append(Flight(cities["Alexandria"], cities["New York"], Time(
        2, 00), Time(15, 14), "MS007", [Days.sun, Days.tue, Days.thu]))
    flights.append(Flight(cities["Aswan"], cities["Cairo"], Time(10, 20), Time(
        11, 40), "MS022", [Days.sat, Days.sun, Days.mon, Days.wed]))
    flights.append(Flight(cities["Aswan"], cities["Port Said"], Time(
        7, 5), Time(8, 18), "MS023", [Days.tue, Days.thu, Days.fri]))
    flights.append(Flight(cities["Cairo"], cities["Alexandria"], Time(
        13, 00), Time(13, 45), "MS008", [Days.sun, Days.mon, Days.wed]))
    flights.append(Flight(cities["Cairo"], cities["Alexandria"], Time(
        20, 15), Time(21, 00), "MS009", [Days.thu, Days.fri]))
    flights.append(Flight(cities["Cairo"], cities["Aswan"], Time(
        8, 00), Time(9, 20), "MS010", [Days.sun, Days.wed]))
    flights.append(Flight(cities["Cairo"], cities["Aswan"], Time(
        17, 15), Time(18, 35), "MS011", [Days.sat, Days.tue, Days.thu]))
    flights.append(Flight(cities["Cairo"], cities["London"], Time(
        10, 00), Time(15, 10), "MS014", [Days.sun, Days.mon, Days.tue]))
    flights.append(Flight(cities["Cairo"], cities["London"], Time(
        15, 15), Time(20, 25), "MS015", [Days.sat, Days.wed, Days.thu]))
    flights.append(Flight(cities["Cairo"], cities["New York"], Time(
        3, 00), Time(15, 5), "MS016", [Days.sat, Days.sun, Days.wed]))
    flights.append(Flight(cities["Cairo"], cities["New York"], Time(
        19, 30), Time(7, 35), "MS017", [Days.mon, Days.tue, Days.fri]))
    flights.append(Flight(cities["Cairo"], cities["Paris"], Time(
        2, 00), Time(6, 55), "MS018", [Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Cairo"], cities["Paris"], Time(
        5, 00), Time(9, 55), "MS019", [Days.sat, Days.mon]))
    flights.append(Flight(cities["Cairo"], cities["Port Said"], Time(
        11, 00), Time(11, 20), "MS013", [Days.mon]))
    flights.append(Flight(cities["Cairo"], cities["Port Said"], Time(
        19, 30), Time(19, 50), "MS012", [Days.sat, Days.sun, Days.wed, Days.thu]))
    flights.append(Flight(cities["Cairo"], cities["Rome"], Time(6, 00), Time(
        9, 30), "MS021", [Days.sat, Days.sun, Days.tue, Days.thu]))
    flights.append(Flight(cities["Cairo"], cities["Shanghai"], Time(
        5, 30), Time(19, 00), "MS020", [Days.sat, Days.sun, Days.mon, Days.wed]))
    flights.append(Flight(cities["Chicago"], cities["London"], Time(
        8, 00), Time(18, 32), "DL050", [Days.sun, Days.tue, Days.thu, Days.fri]))
    flights.append(Flight(cities["Chicago"], cities["London"], Time(
        12, 10), Time(22, 42), "DL051", [Days.sat, Days.mon, Days.wed]))
    flights.append(Flight(cities["Chicago"], cities["Miami"], Time(10, 00), Time(
        14, 20), "DL046", [Days.sat, Days.sun, Days.mon, Days.fri]))
    flights.append(Flight(cities["Chicago"], cities["Miami"], Time(
        17, 20), Time(21, 40), "DL047", [Days.sun, Days.tue]))
    flights.append(Flight(cities["Chicago"], cities["New York"], Time(
        9, 00), Time(11, 18), "DL044", [Days.sat, Days.mon, Days.wed, Days.fri]))
    flights.append(Flight(cities["Chicago"], cities["New York"], Time(
        15, 00), Time(17, 18), "DL045", [Days.sun, Days.tue]))
    flights.append(Flight(cities["Chicago"], cities["Paris"], Time(5, 00), Time(
        16, 55), "DL052", [Days.sat, Days.sun, Days.tue, Days.thu]))
    flights.append(Flight(cities["Chicago"], cities["San Francisco"], Time(
        16, 00), Time(22, 10), "DL048", [Days.thu, Days.fri]))
    flights.append(Flight(cities["Chicago"], cities["San Francisco"], Time(
        20, 00), Time(2, 10), "DL049", [Days.sun, Days.mon, Days.tue]))
    flights.append(Flight(cities["Edinburgh"], cities["London"], Time(7, 00), Time(
        8, 15), "BA128", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Edinburgh"], cities["London"], Time(19, 15), Time(
        20, 30), "BA129", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Edinburgh"], cities["Paris"], Time(14, 00), Time(
        15, 50), "BA130", [Days.sat, Days.mon, Days.tue, Days.wed, Days.fri]))
    flights.append(Flight(cities["Edinburgh"], cities["San Francisco"], Time(
        3, 00), Time(15, 10), "BA131", [Days.sat, Days.sun, Days.mon, Days.thu]))
    flights.append(Flight(cities["Liverpool"], cities["London"], Time(
        4, 30), Time(5, 30), "BA125", [Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Liverpool"], cities["London"], Time(10, 00), Time(
        11, 00), "BA123", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Liverpool"], cities["London"], Time(
        16, 00), Time(17, 00), "BA124", [Days.sat, Days.sun, Days.mon]))
    flights.append(Flight(cities["London"], cities["Alexandria"], Time(
        6, 00), Time(11, 20), "BA149", [Days.sun, Days.mon, Days.wed]))
    flights.append(Flight(cities["London"], cities["Cairo"], Time(10, 00), Time(
        14, 40), "BA143", [Days.sat, Days.sun, Days.tue, Days.fri]))
    flights.append(Flight(cities["London"], cities["Cairo"], Time(
        20, 00), Time(0, 40), "BA144", [Days.tue, Days.thu]))
    flights.append(Flight(cities["London"], cities["Chicago"], Time(4, 00), Time(
        12, 50), "BA147", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["London"], cities["Edinburgh"], Time(5, 00), Time(
        6, 15), "BA134", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["London"], cities["Edinburgh"], Time(
        17, 00), Time(18, 15), "BA135", [Days.sun, Days.wed, Days.fri]))
    flights.append(Flight(cities["London"], cities["Liverpool"], Time(8, 40), Time(
        9, 40), "BA132", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["London"], cities["Liverpool"], Time(
        21, 00), Time(22, 00), "BA133", [Days.sun, Days.mon, Days.thu, Days.fri]))
    flights.append(Flight(cities["London"], cities["Lyon"], Time(15, 00), Time(
        16, 35), "BA150", [Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["London"], cities["Manchester"], Time(10, 00), Time(
        11, 00), "BA136", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["London"], cities["New York"], Time(5, 00), Time(
        13, 00), "BA138", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["London"], cities["New York"], Time(14, 00), Time(
        22, 00), "BA145", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["London"], cities["Paris"], Time(6, 30), Time(
        7, 40), "BA140", [Days.mon, Days.tue, Days.thu, Days.fri]))
    flights.append(Flight(cities["London"], cities["Paris"], Time(16, 00), Time(
        17, 10), "BA139", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["London"], cities["Rome"], Time(17, 00), Time(
        19, 20), "BA141", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["London"], cities["San Francisco"], Time(15, 30), Time(
        2, 30), "BA146", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["London"], cities["Shanghai"], Time(
        4, 30), Time(15, 30), "BA142", [Days.mon, Days.tue, Days.fri]))
    flights.append(Flight(cities["London"], cities["Shanghai"], Time(11, 00), Time(
        22, 00), "BA137", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["London"], cities["Tokyo"], Time(14, 00), Time(
        1, 40), "BA148", [Days.sat, Days.sun, Days.wed, Days.thu]))
    flights.append(Flight(cities["Lyon"], cities["Nice"], Time(2, 10), Time(3, 00), "AF122", [
                   Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Lyon"], cities["Nice"], Time(13, 30), Time(
        14, 20), "AF121", [Days.sat, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Lyon"], cities["Paris"], Time(9, 00), Time(10, 5), "AF119", [
                   Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Lyon"], cities["Paris"], Time(18, 00), Time(19, 5), "AF120", [
                   Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Manchester"], cities["London"], Time(11, 30), Time(
        12, 30), "BA126", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Manchester"], cities["London"], Time(18, 30), Time(
        19, 30), "BA127", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed]))
    flights.append(Flight(cities["Miami"], cities["Chicago"], Time(
        8, 00), Time(12, 20), "DL056", [Days.mon, Days.wed, Days.fri]))
    flights.append(Flight(cities["Miami"], cities["New York"], Time(
        10, 00), Time(12, 55), "DL053", [Days.sun, Days.mon, Days.tue]))
    flights.append(Flight(cities["Miami"], cities["New York"], Time(
        16, 00), Time(18, 55), "DL054", [Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Miami"], cities["San Francisco"], Time(
        10, 00), Time(16, 25), "DL055", [Days.sat, Days.sun, Days.mon, Days.wed]))
    flights.append(Flight(cities["Milan"], cities["London"], Time(14, 00), Time(
        15, 50), "AZ103", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Milan"], cities["Paris"], Time(10, 00), Time(
        11, 20), "AZ101", [Days.sat, Days.sun, Days.tue, Days.wed]))
    flights.append(Flight(cities["Milan"], cities["Paris"], Time(
        16, 00), Time(17, 20), "AZ102", [Days.mon, Days.fri]))
    flights.append(Flight(cities["Milan"], cities["Rome"], Time(
        1, 00), Time(2, 5), "AZ104", [Days.mon, Days.thu, Days.fri]))
    flights.append(Flight(cities["Milan"], cities["Rome"], Time(7, 00), Time(8, 5), "AZ099", [
                   Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Milan"], cities["Rome"], Time(17, 00), Time(18, 5), "AZ100", [
                   Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["New York"], cities["Chicago"], Time(
        7, 00), Time(9, 18), "DL028", [Days.sat, Days.mon, Days.tue]))
    flights.append(Flight(cities["New York"], cities["Chicago"], Time(
        13, 20), Time(15, 38), "DL029", [Days.sat, Days.sun, Days.thu]))
    flights.append(Flight(cities["New York"], cities["Edinburgh"], Time(
        6, 00), Time(15, 5), "DL038", [Days.sun, Days.wed, Days.fri]))
    flights.append(Flight(cities["New York"], cities["London"], Time(
        4, 00), Time(10, 50), "DL037", [Days.sat, Days.mon, Days.tue, Days.thu]))
    flights.append(Flight(cities["New York"], cities["Lyon"], Time(
        13, 00), Time(22, 12), "DL041", [Days.sat, Days.mon, Days.tue]))
    flights.append(Flight(cities["New York"], cities["Miami"], Time(
        1, 00), Time(3, 55), "DL036", [Days.tue]))
    flights.append(Flight(cities["New York"], cities["Miami"], Time(
        7, 15), Time(10, 10), "DL035", [Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["New York"], cities["Miami"], Time(
        12, 00), Time(14, 55), "DL034", [Days.sat, Days.sun, Days.mon]))
    flights.append(Flight(cities["New York"], cities["Paris"], Time(
        11, 00), Time(17, 50), "DL040", [Days.sun, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["New York"], cities["Rome"], Time(10, 15), Time(
        18, 30), "DL039", [Days.sat, Days.mon, Days.tue, Days.thu]))
    flights.append(Flight(cities["New York"], cities["San Francisco"], Time(
        8, 00), Time(14, 32), "DL030", [Days.sun, Days.mon]))
    flights.append(Flight(cities["New York"], cities["San Francisco"], Time(
        10, 00), Time(16, 32), "DL031", [Days.wed, Days.fri]))
    flights.append(Flight(cities["New York"], cities["San Francisco"], Time(
        18, 00), Time(0, 32), "DL032", [Days.thu]))
    flights.append(Flight(cities["New York"], cities["San Francisco"], Time(
        23, 30), Time(6, 2), "DL033", [Days.sat, Days.tue]))
    flights.append(Flight(cities["New York"], cities["Shanghai"], Time(
        5, 00), Time(19, 50), "DL043", [Days.sat, Days.mon, Days.wed, Days.fri]))
    flights.append(Flight(cities["New York"], cities["Tokyo"], Time(
        0, 00), Time(13, 45), "DL042", [Days.sat, Days.sun, Days.tue, Days.thu]))
    flights.append(Flight(cities["Nice"], cities["Lyon"], Time(20, 00), Time(20, 50), "AF118", [
                   Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Nice"], cities["Paris"], Time(5, 00), Time(6, 20), "AF117", [
                   Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Nice"], cities["Paris"], Time(
        14, 30), Time(15, 50), "AF116", [Days.sat, Days.sun, Days.fri]))
    flights.append(Flight(cities["Paris"], cities["London"], Time(9, 00), Time(
        10, 5), "AF105", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Paris"], cities["London"], Time(22, 00), Time(
        23, 5), "AF106", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Paris"], cities["Lyon"], Time(7, 00), Time(
        8, 10), "AF114", [Days.mon, Days.tue, Days.wed, Days.thu]))
    flights.append(Flight(cities["Paris"], cities["Lyon"], Time(14, 00), Time(
        15, 10), "AF115", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Paris"], cities["New York"], Time(12, 00), Time(
        20, 30), "AF107", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Paris"], cities["New York"], Time(
        17, 30), Time(2, 00), "AF108", [Days.sat, Days.sun, Days.fri]))
    flights.append(Flight(cities["Paris"], cities["Nice"], Time(11, 00), Time(12, 20), "AF112", [
                   Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Paris"], cities["Nice"], Time(16, 00), Time(17, 20), "AF113", [
                   Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Paris"], cities["Rome"], Time(10, 00), Time(12, 00), "AF110", [
                   Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Paris"], cities["Rome"], Time(18, 00), Time(
        20, 00), "AF109", [Days.sun, Days.tue, Days.wed, Days.fri]))
    flights.append(Flight(cities["Paris"], cities["Shanghai"], Time(
        4, 00), Time(15, 55), "AF111", [Days.sat, Days.mon]))
    flights.append(Flight(cities["Port Said"], cities["Alexandria"], Time(
        12, 00), Time(12, 30), "MS026", [Days.sun, Days.mon, Days.wed]))
    flights.append(Flight(cities["Port Said"], cities["Alexandria"], Time(
        14, 45), Time(15, 15), "MS027", [Days.sat, Days.tue, Days.thu]))
    flights.append(Flight(cities["Port Said"], cities["Cairo"], Time(
        11, 00), Time(11, 20), "MS024", [Days.sat, Days.mon]))
    flights.append(Flight(cities["Port Said"], cities["Cairo"], Time(
        14, 10), Time(14, 30), "MS025", [Days.wed, Days.fri]))
    flights.append(Flight(cities["Rome"], cities["London"], Time(1, 00), Time(3, 30), "AZ091", [
                   Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Rome"], cities["London"], Time(11, 30), Time(
        14, 00), "AZ090", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Rome"], cities["Milan"], Time(8, 00), Time(9, 5), "AZ094", [
                   Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Rome"], cities["Milan"], Time(22, 00), Time(
        23, 5), "AZ095", [Days.mon, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Rome"], cities["New York"], Time(4, 00), Time(
        13, 48), "AZ088", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Rome"], cities["New York"], Time(
        17, 00), Time(2, 48), "AZ089", [Days.tue, Days.wed, Days.fri]))
    flights.append(Flight(cities["Rome"], cities["Paris"], Time(8, 00), Time(10, 00), "AZ086", [
                   Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Rome"], cities["Paris"], Time(20, 00), Time(
        22, 00), "AZ087", [Days.mon, Days.tue, Days.thu, Days.fri]))
    flights.append(Flight(cities["Rome"], cities["Venice"], Time(11, 00), Time(
        12, 00), "AZ092", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Rome"], cities["Venice"], Time(18, 00), Time(
        19, 00), "AZ093", [Days.sat, Days.mon, Days.wed, Days.fri]))
    flights.append(Flight(cities["San Francisco"], cities["Chicago"], Time(
        7, 00), Time(13, 10), "DL059", [Days.tue, Days.wed, Days.thu]))
    flights.append(Flight(cities["San Francisco"], cities["Chicago"], Time(
        14, 00), Time(20, 10), "DL060", [Days.sat, Days.sun, Days.fri]))
    flights.append(Flight(cities["San Francisco"], cities["Miami"], Time(
        11, 00), Time(17, 25), "DL061", [Days.sun, Days.mon, Days.wed, Days.thu]))
    flights.append(Flight(cities["San Francisco"], cities["New York"], Time(
        6, 00), Time(12, 32), "DL057", [Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["San Francisco"], cities["New York"], Time(
        13, 00), Time(19, 32), "DL058", [Days.sat, Days.sun, Days.mon]))
    flights.append(Flight(cities["Shanghai"], cities["Cairo"], Time(2, 00), Time(
        16, 30), "CA070", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Cairo"], Time(7, 00), Time(
        21, 30), "CA068", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Cairo"], Time(13, 30), Time(
        4, 00), "CA069", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Chicago"], Time(6, 00), Time(
        19, 45), "CA080", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Chicago"], Time(15, 00), Time(
        4, 45), "CA081", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["London"], Time(0, 40), Time(
        13, 20), "CA071", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["London"], Time(5, 30), Time(
        18, 10), "CA072", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["London"], Time(14, 00), Time(
        2, 40), "CA073", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["New York"], Time(1, 00), Time(
        15, 50), "CA079", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["New York"], Time(10, 00), Time(
        0, 50), "CA078", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Paris"], Time(2, 00), Time(
        14, 25), "CA076", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Paris"], Time(8, 00), Time(
        20, 25), "CA077", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Rome"], Time(6, 00), Time(
        19, 10), "CA074", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Rome"], Time(17, 00), Time(
        6, 10), "CA075", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Tokyo"], Time(5, 00), Time(
        7, 50), "CA085", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Tokyo"], Time(12, 00), Time(
        14, 50), "CA082", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Tokyo"], Time(16, 00), Time(
        18, 50), "CA083", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Shanghai"], cities["Tokyo"], Time(21, 00), Time(
        23, 50), "CA084", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Tokyo"], cities["San Francisco"], Time(12, 00), Time(
        21, 5), "JL066", [Days.sat, Days.sun, Days.mon, Days.wed, Days.thu]))
    flights.append(Flight(cities["Tokyo"], cities["San Francisco"], Time(22, 00), Time(
        7, 5), "JL067", [Days.sat, Days.mon, Days.tue, Days.thu, Days.fri]))
    flights.append(Flight(cities["Tokyo"], cities["Shanghai"], Time(
        0, 00), Time(2, 50), "JL063", [Days.sun, Days.tue, Days.thu, Days.fri]))
    flights.append(Flight(cities["Tokyo"], cities["Shanghai"], Time(
        6, 10), Time(9, 00), "JL064", [Days.sun, Days.mon, Days.tue, Days.wed]))
    flights.append(Flight(cities["Tokyo"], cities["Shanghai"], Time(
        9, 00), Time(11, 50), "JL065", [Days.sat, Days.thu, Days.fri]))
    flights.append(Flight(cities["Tokyo"], cities["Shanghai"], Time(
        20, 00), Time(22, 50), "JL062", [Days.sat, Days.sun, Days.mon, Days.wed]))
    flights.append(Flight(cities["Venice"], cities["Rome"], Time(5, 00), Time(6, 00), "AZ096", [
                   Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Venice"], cities["Rome"], Time(14, 00), Time(
        15, 00), "AZ097", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    flights.append(Flight(cities["Venice"], cities["Rome"], Time(19, 40), Time(
        20, 40), "AZ098", [Days.sat, Days.sun, Days.mon, Days.tue, Days.wed, Days.thu, Days.fri]))
    return flights


if __name__ == '__main__':
    main()
