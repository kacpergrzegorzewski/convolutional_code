import sys


def read_bits(filename):
    file = open(filename, 'r')
    data = file.read()
    file.close()
    return data


def save_data(filename, data):
    with open(filename, 'w') as file:
        file.write(data)


class Encoder:
    register_length = 9

    def __init__(self, data):
        self.data = data
        self.register = list(self.register_length * "0")

    # shift register
    def _shift(self, next_bit):
        i = self.register_length - 1
        while i > 0:
            self.register[i] = self.register[i - 1]
            i = i - 1
        self.register[0] = next_bit

    # add with modulo 2
    def _add(self, bits):
        result = 0
        for bit in bits:
            result = result + bit
        result = result % 2
        return result

    # single round of generating 3 bits of output from register
    # based on http://www.wirelesscommunication.nl/reference/chaptr01/telephon/is95/is95rev.htm
    def _generate_output(self):
        register = list(map(int, self.register))  # convert all elements to int so we can add them easily
        g0 = [register[0], register[2], register[3], register[5], register[6], register[7], register[8]]
        g1 = [register[0], register[1], register[3], register[4], register[7], register[8]]
        g2 = [register[0], register[1], register[2], register[5], register[8]]

        c0 = self._add(g0)
        c1 = self._add(g1)
        c2 = self._add(g2)

        result = [c0, c1, c2]

        return list(map(str, result))  # return string

    def encode(self):
        result = self._generate_output()

        for bit in self.data:
            self._shift(bit)
            result += self._generate_output()

        # clear register
        for i in range(0, self.register_length):
            self._shift('0')
            result += self._generate_output()

        return result


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

    data = read_bits(input)
    encoder = Encoder(data)
    save_data(output, ''.join(encoder.encode()))    # convert array to one string
