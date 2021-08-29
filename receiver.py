import sys

BMP_HEADER_LENGTH = 40  # bytes


def get_bytes_from_file(filename):
    array_of_bytes = []
    with open(filename, 'r') as file:
        data = file.read()
        array_of_bytes = get_bytes(data)

    return array_of_bytes


def get_bytes(data):
    array_of_bytes = []
    string_byte = ""
    i = 0
    for bit in data:
        string_byte = string_byte + bit
        i = i + 1
        if i == 8:
            array_of_bytes.append(int(string_byte, 2))
            string_byte = ""
            i = 0

    return array_of_bytes


def byte_to_char(data):
    result = ""
    for byte in data:
        result += chr(byte)
    return result


def binary_to_string(binary):
    bytes = get_bytes(binary)
    return byte_to_char(bytes)


def save_data_binary(filename, data):
    data = bytearray(data)
    file = open(filename, 'wb')
    file.write(data)
    file.close()


def obtain_file_type(filename):
    filetype = filename.split(".")[-1]
    return filetype


def get_bmp_header(bmp_header_file):
    with open(bmp_header_file, 'rb') as file:
        header = file.read(BMP_HEADER_LENGTH)
    return list(header)


def binary_to_readable_file(transmission_line, output, bmp_header_file):
    filetype = obtain_file_type(output)
    data = []
    if filetype == "bmp":
        if bmp_header_file is None:
            print("NO BMP HEADER FOUND. EXITING...")
            exit(3)
        data = data + get_bmp_header(bmp_header_file)
        data = data + get_bytes_from_file(transmission_line)
    elif filetype == "txt":
        data = data + get_bytes_from_file(transmission_line)
    save_data_binary(output, data)


def count_ber(input_bits, output_bits):
    if len(input_bits) != len(output_bits):
        raise ValueError("Lengths are not the same!")
    length = len(input_bits)
    counter = 0
    i = 0
    for bit in input_bits:
        if bit != output_bits[i]:
            counter += 1
        i += 1
    return counter/length


if __name__ == '__main__':
    try:
        input = sys.argv[1]
        output = sys.argv[2]
    except Exception as e:
        print("Expected 2 arguments but found " + str(len(sys.argv) - 1) + ".")
        print(e)
        input = None
        output = None
        exit(2)
    try:
        bmp_header = sys.argv[3]
        print("taking bitmap header from " + bmp_header)
    except:
        bmp_header = None

    binary_to_readable_file(input, output, bmp_header)
