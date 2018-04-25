import csv
import datetime
import queue
import threading
import time
import bs4


def log(message):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print("%s %s" % (now, message))


class Factory:
    THREAD_NUMBER = 3
    task_queue = queue.Queue()

    def __init__(self):
        try:
            self.vehicles_from_csv = Factory.read_csv()
            for i in range(self.THREAD_NUMBER):
                ProductionLine(i, self.task_queue).start()
            self.run()
        except FileNotFoundError:
            print("Sprawdz czy plik CSV znajduje sie w katalogu lub czy ma poprawne dane")
            pass

    def run(self):
        while True:
            vehicles_orders = Factory.get_orders()
            log("Poczatek pracy")
            for ve in vehicles_orders:
                vehicle = Vehicle(ve, self.vehicles_from_csv)
                try:
                    self.task_queue.put(vehicle.time)
                except AttributeError:
                    print("Nie mozna wyprodukowac pojazdu o nazwie "+str(ve))
            self.task_queue.join()
            log("Wszystkie linie produkcyjne zakonczyly prace")
            print("Laczny koszt produkcji: " + str(Vehicle.total_cost))

    @staticmethod
    def read_csv():
        vehicles = []
        with open("vehicles.csv") as file:
            reader = csv.DictReader(file)
            for line in reader:
                vehicles.append(line)
        return vehicles

    @staticmethod
    def get_orders():
        input_data = input("Podaj zlecenia dla fabryki \n")
        soup = bs4.BeautifulSoup(input_data, "xml")
        orders = soup.findAll('item', type=True)
        vehicles_list = []
        for order in orders:
            vehicles_list.append(order["type"])
        return vehicles_list


class Vehicle:
    total_cost = 0

    def __init__(self, type, vehicles):
        for veh in vehicles:
            if veh["Typ pojazdu"] == type:
                self.time = int(veh["Czas produkcji"])
                Vehicle.add_cost(int(veh["Koszt produkcji"]))

    @staticmethod
    def add_cost(cost):
        Vehicle.total_cost += cost


class ProductionLine(threading.Thread):
    def __init__(self, nr, task_queue):
        threading.Thread.__init__(self, name="Linia produkcyjna nr %d" % (nr,))
        self.task_queue = task_queue

    def run(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                break
            log("%s %s sekund pracy" % (self.getName(), task))
            time.sleep(task)
            self.task_queue.task_done()
            log("%s koniec pracy" % (self.getName()))


if __name__ == "__main__":
    Factory()

