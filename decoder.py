import sys


def read_bits(filename):
    file = open(filename, 'r')
    data = file.read()
    file.close()
    return data


def save_data(filename, data):
    with open(filename, 'w') as file:
        file.write(data)


# Hamming distance between a and b
def hamming_distance(a, b):
    distance = 0
    for char in range(0, len(a)):
        if a[char] != b[char]:
            distance += 1
    return distance


# add with modulo 2
def add(bits):
    result = 0
    for bit in bits:
        result = result + bit
    result = result % 2
    return result


class Decoder:

    def __init__(self, data, traceback_depth):
        self.active_states = []
        self.register_length = 8
        self.data = data
        # Trellis structure:
        # index - number of state
        # value - [input_to_this_state, [weights]]
        self.trellis = []
        # All states in time t+1
        self.next_time = [["", []] for i in range(0, (2 ** self.register_length))]
        self.all_output = self.generate_all_possible_output()
        self.max_traceback_depth = traceback_depth
        self.current_traceback_depth = 0

        # Most probable bit stream
        self.decoded_data = ""

    def _next_time(self):
        self.trellis = []
        self.trellis += self.next_time
        self.next_time = [["", []] for _ in range(0, (2 ** self.register_length))]

    def _set_input(self, input, index):
        self.next_time[index][0] = input

    def _set_weight(self, weight, index):
        self.next_time[index][1] = weight

    def _is_weight_lower(self, current_state, next_state, weight):
        new_weight = sum(self.trellis[current_state][1]) + weight
        previous_weight = sum(self.next_time[next_state][1])
        # If new weight is lower or previous weight doesn't exist (no path to this state)
        if new_weight < previous_weight or self.next_time[next_state][0] == "":
            return True
        return False

    # Delete first weights and all bad paths.
    # Correct_bit is most probable decoded bit.
    def _clear_tree(self, correct_bit):
        for index in range(0, len(self.trellis)):
            if self._check_first_bit(index) == correct_bit:
                self.trellis[index][1].pop(0)
                self.trellis[index][0] = self.trellis[index][0][1:]
            else:
                self._clear_state(index)

    # Clear path and weights in state index
    def _clear_state(self, index):
        self.trellis[index] = ["", []]

    # Return first bit of state index
    def _check_first_bit(self, index):
        if len(self.trellis[index][0]) == 0:
            return None
        return self.trellis[index][0][0]

    # Returns most probable bits
    def _find_best_bits(self):
        best_bits = 0
        best_weight = -1
        for state in self.trellis:
            if state[0] != "":
                # Sum of all weights
                weight = sum(state[1])
                if weight < best_weight or best_weight == -1:
                    best_weight = weight
                    best_bits = state[0]
        # All states are empty
        if best_weight == -1:
            exit(2)
        return best_bits

    def decode(self):
        # Clear trellis
        self._next_time()

        # starting in state 0
        self.active_states.append(0)
        self._next_time()

        # data should be a multiple of 3
        for i in range(1, int(len(self.data) / 3)):
            # Take 3 next bits every time
            current_data = self.data[3 * i:3 * i + 3]
            # temporary active states for the loop (avoiding taking later states)
            active_states = []
            active_states += self.active_states
            if i % 1000 == 0:
                print(str(300 * i / len(self.data))[:4] + "%")

            for state in active_states:
                # input = 0
                self._decode_single_state(state, "0", current_data)
                # input = 1
                self._decode_single_state(state, "1", current_data)

            self._next_time()
            self.current_traceback_depth += 1

            if self.current_traceback_depth == self.max_traceback_depth:
                best_bit = self._find_best_bits()[0]
                self.decoded_data += best_bit
                self._clear_tree(best_bit)
                self.active_states = self._find_active_states()
                self.current_traceback_depth -= 1

        # Add last bits without traceback depth rule
        best_bits = self._find_best_bits()
        self.decoded_data += best_bits

        return self.decoded_data

    def _decode_single_state(self, state, input, current_data):
        # current state with input
        current_register = input + bin(state)[2:].zfill(self.register_length)
        # next state as integer (current state with input without last bit = shift)
        next_state = int(current_register[:-1], 2)
        # distance between encoded and received data
        weight = hamming_distance(self.all_output[int(current_register, 2)], current_data)

        if self._is_weight_lower(state, next_state, weight):
            self._set_input(self.trellis[state][0] + input, next_state)
            self._set_weight(self.trellis[state][1] + [weight], next_state)
            self.active_states.append(next_state)

    def _find_active_states(self):
        active_states = []
        for index in range(0, len(self.trellis)):
            if self.trellis[index][0] != "":
                active_states.append(index)
        return active_states

    # Generates array of every possible output from register input
    def generate_all_possible_output(self):
        result = []
        for i in range(0, 2 ** (self.register_length + 1)):
            result.append(self._generate_output(bin(i)[2:].zfill(self.register_length + 1)))

        return result

    # single round of generating 3 bits of output from register (with input bit)
    # based on http://www.wirelesscommunication.nl/reference/chaptr01/telephon/is95/is95rev.htm
    def _generate_output(self, register):
        register = list(map(int, register))  # convert all elements to int so we can add them easily
        g0 = [register[0], register[2], register[3], register[5], register[6], register[7], register[8]]
        g1 = [register[0], register[1], register[3], register[4], register[7], register[8]]
        g2 = [register[0], register[1], register[2], register[5], register[8]]

        c0 = add(g0)
        c1 = add(g1)
        c2 = add(g2)

        result = str(c0) + str(c1) + str(c2)

        return result  # return string


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

    decoder = Decoder(read_bits(input), 15)

    save_data(output, decoder.decode())
