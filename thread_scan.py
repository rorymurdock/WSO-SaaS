"""Multi-threaded version of the instance scanner"""
import threading
import random
from instance import CheckInstance

OUTPUT = 'csv'
MAX_THREADS = 10
MAX_INSTANCE = 5000

def list_splitter(instances, threads):
    """Take the instance, range it and split into equal threads"""
    instances = list(range(instances))

    # Randomise range to avoid some threads closing early with lots of blanks
    random.shuffle(instances)

    for i in range(0, len(instances), threads):
        yield instances[i:i+threads]

def check_instance(instance_list):
    """Iterate through the list and check the instance"""
    for instance in instance_list:
        saas = CheckInstance(instance)
        if not saas.check_hostname_valid():
            print(saas.format_output(output=OUTPUT))
        else:
            saas.get_version()
            saas.check_redirection()
            saas.get_location()
            print(saas.format_output(output=OUTPUT))

def start():
    """Start the threads"""
    split = list(list_splitter(MAX_INSTANCE, MAX_THREADS))

    threads = list()
    for index in range(MAX_THREADS):
        thread = threading.Thread(target=check_instance, args=(split[index],))
        threads.append(thread)
        thread.start()

    for index, thread in enumerate(threads):
        thread.join()

if __name__ == "__main__":
    start()
