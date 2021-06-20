import sys

BMP_HEADER_LENGTH = 14  # bytes


def get_ascii_binary(filename):
    with open(filename, 'r') as file:
        data = file.read()
        result = ""
        for char in data:
            result = result + bin(ord(char))[2:].zfill(8)
    return result


def get_bmp_data(filename):
    with open(filename, 'rb') as file:
        file.read(BMP_HEADER_LENGTH)
        byte = file.read(1)
        result = ""
        while byte:
            result = result + bin(int(byte.hex(), 16))[2:].zfill(8)
            byte = file.read(1)
    return result


def get_binary(filename):
    with open(filename, 'rb') as file:
        result = ""
        byte = file.read(1)
        while byte:
            result = result + bin(int(byte.hex(), 16))[2:].zfill(8)
            byte = file.read(1)
    return result


def save_data(filename, data):
    with open(filename, 'w') as file:
        file.write(data)


def obtain_file_type(filename):
    filetype = filename.split(".")[-1]
    return filetype


def generate_binary_source(input, output):
    filetype = obtain_file_type(input)
    if filetype == "txt":
        save_data(output, get_ascii_binary(input))
    elif filetype == "bmp":
        save_data(output, get_bmp_data(input))
    else:
        save_data(output, get_binary(input))


if __name__ == '__main__':
    input = sys.argv[1]
    output = sys.argv[2]

    generate_binary_source(input, output)
