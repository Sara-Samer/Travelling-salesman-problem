import math
import enum


class Node:
    def __init__(self, city="", timeCost=0, hueristicCost=0, visited=[]):
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
        return ("in: " + self.city + " cost is: " + self.totalCost)


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
        h = (str(self.hours) if self.hours > 9 else "0" + str(self.hours))
        m = (str(self.minutes) if self.minutes > 9 else "0" + str(self.minutes))
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
        return ("City: " + self.city)

    def __eq__(self, other):
        return self.city == other.city


class Flight:
    def __init__(self, departureTime, arrivalTime, name, days):
        self.departureTime = departureTime
        self.arrivalTime = arrivalTime
        self.name = name
        self.days = days

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return ("name: " + self.name + " departure time " + self.departureTime + " and arrival time " + self.arrivalTime)
        # return ("name: " + self.name+" duration is: " + str(self.getDuration()))

    def getDays(self):
        return self.days

    def getDuration(self):
        return self.arrivalTime - self.departureTime


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
        return ("from " + str(self.cityFrom) + " to " + str(self.cityTo) + " flights: " + str(self.flights))


def getFlights(names, flights):
    return [flight for flight in flights if flight.name in names]


def getAvailableCities(city, timeTables):
    return [table for table in timeTables if city == table.getCityFrom()]


def addToOpen(_next, _open):
    for node in _open:
        if (_next == node and _next.totalCost >= node.totalCost):
            return False
    return True


def alreadyInClosed(_next, closed):
    for node in closed:
        if (_next == node and _next.totalCost >= node.totalCost):
            return True
    return False


def travel(start, goal, startDay, endDay, flights, timeTables):
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
                d += 1
                day = Days(d)
                time = Time(minutes=(time - fullDay))

            # For printing the path
            lastVisited = list(currentNode.getVisited())

            # Add current node as visited
            closed.append(currentNode)

            # If it's the goal add to possible paths then break out of the loop
            if currentNode == goal:
                paths.append(currentNode)
                break
            # If not then get children of current node
            children = getAvailableCities(currentCity, timeTables)

            # And for each child calculate hueristic and cost then append to open list
            for child in children:

                # This loop iterates only on flights that are available in current day
                for flight in child.getFlights():

                    # For each flight of make it takes of in current day
                    if day not in flight.getDays():
                        continue

                    nextCity = child.getCityTo()
                    # calculate hueristic from distance
                    hueristic = currentCity.getDistanceFrom(nextCity)

                    # calculate flight cost
                    # if it's the first time don't calculate waiting time
                    if(currentNode == start):
                        cost = flight.getDuration()
                        time = flight.arrivalTime
                    else:
                        # First calculate waiting time
                        # which is  time since arrival of last flight - departure of current flight
                        # cost is flight duration + waiting time
                        # and the time is increased by the flight duration and waiting time
                        waitingTime = time - flight.departureTime
                        cost = flight.getDuration() + waitingTime
                        time = time.add(flight.getDuration()) + waitingTime

                    # Keeping track of the path
                    text = "\nfrom " + currentCity.getName() + " To " + nextCity.getName() + \
                        " using flight " + str(flight)
                    # create node with the city, flight and costs
                    node = Node(nextCity, cost, hueristic,
                                lastVisited.append(text))

                    # If it's already visited then don't add and search for others
                    if alreadyInClosed(node, closed):
                        continue

                    if addToOpen(node, _open):
                        _open.append(node)
    paths.sort()
    return paths


class Days(enum.Enum):
    Sat = 1
    Sun = 2
    Mon = 3
    Tue = 4
    Wed = 5
    Thu = 6
    Fri = 7


def main():
    cities = {}
    flights = []
    timeTables = []

    cities['Egypt'] = City('Egypt', 0, 0)
    cities['UK'] = City('UK', 1, 0)
    cities['USA'] = City('USA', 0, 1)
    cities['Japan'] = City('Japan', 1, 1)

    flights.append(Flight(Time(11, 00), Time(
        18, 30), 'n60', [Days.Mon, Days.Sat]))
    flights.append(Flight(Time(7, 00), Time(
        16, 30), 'n70', [Days.Sun, Days.Mon]))
    flights.append(Flight(Time(6, 00), Time(
        12, 56), 'n315', [Days.Tue, Days.Fri]))
    flights.append(Flight(Time(3, 00), Time(
        7, 45), 'f180', [Days.Thu, Days.Sat]))
    timeTables.append(
        TimeTable(cities['Egypt'], cities['UK'], getFlights(['n60', 'f180'], flights)))
    timeTables.append(
        TimeTable(cities['Egypt'], cities['USA'], getFlights(['n70', 'n315'], flights)))
    timeTables.append(
        TimeTable(cities['Japan'], cities['USA'], getFlights(['n60', 'n70'], flights)))

    # start = input("Enter start city: ")
    # destination = input("Enter destination city: ")
    # print("Days: Sat, Sun, Mon, Tue, Wed, Thu and Fri")
    # startDay = Days[input("Enter start day: ")]
    # endDay = Days[input("Enter end day: ")]
    # travel(start, destination, startDay, endDay, flights, timeTables)


if __name__ == '__main__':
    main()
