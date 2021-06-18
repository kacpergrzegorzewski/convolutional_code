import sys


def get_binary_ascii(filename):
    with open(filename, 'r') as file:
        data = file.read()
        result = ""
        for char in data:
            result = result + bin(ord(char))[2:].zfill(8)
    return result


def save_data(filename, data):
    with open(filename, 'w') as file:
        file.write(data)


def obtain_file_type(filename):



if __name__ == '__main__':
    input = sys.argv[1]
    output = sys.argv[2]
    save_data(output, get_binary_ascii(input))
