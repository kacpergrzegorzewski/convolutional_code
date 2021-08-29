import sys
from random import randrange


def save_data(filename, data):
    with open(filename, 'w') as file:
        file.write(data)


def burst_noise(data, first_bit, number_of_bits):
    print("not implemented yet")


def read_transmission_line(filename):
    file = open(filename, 'r')
    data = file.read()
    file.close()
    return data


def random_true(probability):
    number = randrange(probability)
    if number == 0:
        return True
    return False


def convert_probability(probability):
    if "/" in probability:
        nominator = int(probability.split('/')[0])
        denominator = int(probability.split('/')[1])
        probability = int(denominator / nominator)  # easier to operate with int than with float
    elif "." in probability:
        probability = int(1 / float(probability))  # same
    else:
        raise ValueError("Wrong Probability")
    return probability


def make_noise(data, probability, number_of_bits=None):
    if type(probability) is str:
        probability = convert_probability(probability)

    if number_of_bits is not None:
        number_of_bits = int(number_of_bits)
    counter = 0

    new_data = ""
    for bit in data:
        if random_true(probability):
            new_bit = str((int(bit) + 1) % 2)
        else:
            new_bit = bit
        new_data = new_data + new_bit
        counter = counter + 1
        if number_of_bits is not None and counter == number_of_bits:
            new_data = new_data + data[number_of_bits:]
            break

    return new_data


if __name__ == '__main__':
    try:
        input = sys.argv[1]
        output = sys.argv[2]
        probability = sys.argv[3]
    except Exception as e:
        print("Expected 3 arguments but found " + str(len(sys.argv) - 1) + ".")
        print(e)
        input = None
        output = None
        probability = None
        exit(2)
    try:
        number_of_bits = sys.argv[4]
        print("taking " + number_of_bits + " first bits")
    except:
        number_of_bits = None

    data = read_transmission_line(input)
    new_data = make_noise(data, probability, number_of_bits)
    save_data(output, new_data)
