from tkinter import *
from tkinter.scrolledtext import ScrolledText
from source_generator import char_to_bin
from noise_generator import make_noise, convert_probability
from encoder import Encoder
from receiver import binary_to_string, count_ber
from decoder import Decoder


class App(Frame):
    SIZE = "1200x720"
    ERROR_COLOR = "#e57373"
    TRACEBACK_DEPTH = 100

    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        self.root.geometry(self.SIZE)
        self.grid()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=5)
        self.root.rowconfigure(1, weight=5)
        self.root.rowconfigure(2, weight=80)
        self.root.rowconfigure(3, weight=10)
        self.create_widgets()
        self.build()
        self.probability = ""
        self.received_bits_without_coding = ""
        self.received_bits_with_coding = ""

    def create_widgets(self):
        # top
        self.top_frame = Frame(self.root,
                               pady=20,
                               )
        self.top_frame.columnconfigure(0, weight=1)

        self.change_mode_button = Button(self.top_frame,
                                         text="change mode",
                                         pady=20,
                                         anchor=CENTER
                                         )

        # probability
        self.probability_frame = Frame(self.root,
                                       )
        self.probability_title = Label(self.probability_frame,
                                       text="Bit error rate:"
                                       )
        self.probability_box = Text(self.probability_frame,
                                    width=10,
                                    height=1,
                                    bg="#e57373"
                                    )
        self.probability_box.bind("<KeyRelease>", self.key_release_probability)

        # text mode
        self.text_mode_frame = Frame(self.root,
                                     )
        self.text_mode_frame.columnconfigure(0, weight=1)
        self.text_mode_frame.columnconfigure(1, weight=1)
        self.text_mode_frame.columnconfigure(2, weight=1)
        self.text_mode_frame.rowconfigure(0, weight=1)

        # input
        self.input_frame = Frame(self.text_mode_frame)
        input_output_width = 40
        input_output_height = 5
        self.input_title = Label(self.input_frame,
                                 text="Input:",
                                 anchor=W,
                                 width=input_output_width
                                 )

        self.input_box = ScrolledText(self.input_frame,
                                      width=input_output_width,
                                      height=input_output_height
                                      )
        self.input_box.bind("<KeyRelease>", self.key_release_input)

        self.input_ber_label = Label(self.input_frame,
                                     text="BER=0"
                                     )

        self.source_frame = Frame(self.input_frame,
                                  pady=20
                                  )
        self.source_box = Text(self.source_frame,
                               width=input_output_width,
                               height=input_output_height * 4,
                               bg="#F0F0F0",
                               state=DISABLED,
                               bd=0
                               )
        # without coding
        self.output_without_coding_frame = Frame(self.text_mode_frame)
        self.output_without_coding_title = Label(self.output_without_coding_frame,
                                                 text="Output without coding:",
                                                 anchor=W,
                                                 width=input_output_width,
                                                 )
        self.output_without_coding_box = ScrolledText(self.output_without_coding_frame,
                                                      width=input_output_width,
                                                      height=input_output_height,
                                                      state=DISABLED
                                                      )
        self.ber_without_coding_label = Label(self.output_without_coding_frame,
                                              text="BER=0"
                                              )

        self.source_without_coding_frame = Frame(self.output_without_coding_frame,
                                                 pady=20
                                                 )
        self.source_without_coding_box = Text(self.source_without_coding_frame,
                                              width=input_output_width,
                                              height=input_output_height * 4,
                                              bg="#F0F0F0",
                                              state=DISABLED,
                                              bd=0
                                              )

        # with coding
        self.output_with_coding_frame = Frame(self.text_mode_frame)
        self.output_with_coding_title = Label(self.output_with_coding_frame,
                                              text="Output with coding:",
                                              anchor=W,
                                              width=input_output_width,
                                              )
        self.output_with_coding_box = ScrolledText(self.output_with_coding_frame,
                                                   width=input_output_width,
                                                   height=input_output_height,
                                                   state=DISABLED
                                                   )

        self.ber_with_coding_label = Label(self.output_with_coding_frame,
                                           text="BER=0"
                                           )

        self.source_with_coding_frame = Frame(self.output_with_coding_frame,
                                              pady=20
                                              )
        self.source_with_coding_box = Text(self.source_with_coding_frame,
                                           width=input_output_width,
                                           height=input_output_height * 4,
                                           bg="#F0F0F0",
                                           state=DISABLED,
                                           bd=0
                                           )

        # bottom
        self.bottom_frame = Frame(self.root)
        self.run_button = Button(self.bottom_frame,
                                 text="RUN",
                                 width=30,
                                 height=4,
                                 command=self.run
                                 )

    def build(self):
        # top
        self.top_frame.grid(row=0, column=0, )
        self.change_mode_button.grid(row=0, column=0, )

        # probability
        self.probability_frame.grid(row=1, column=0, sticky="w", padx=20, ipady=5)
        self.probability_title.grid(row=0, column=0, padx=4)
        self.probability_box.grid(row=0, column=1)

        # text_mode
        self.text_mode_frame.grid(row=2, column=0, padx=24, sticky="nwse")
        # input
        self.input_frame.grid(row=0, column=0, sticky="n")

        self.input_title.grid(row=0, column=0, sticky="w")
        self.input_box.grid(row=1, column=0)
        self.input_ber_label.grid(row=2, column=0)
        self.source_frame.grid(row=3, column=0, ipady=40)
        self.source_box.grid(row=0, column=0, ipady=20)

        # output without coding
        self.output_without_coding_frame.grid(column=1, row=0, sticky="n")
        self.output_without_coding_title.grid(row=0, column=0, sticky="w")
        self.output_without_coding_box.grid(row=1, column=0)
        self.ber_without_coding_label.grid(row=2, column=0)
        self.source_without_coding_frame.grid(row=3, column=0, ipady=40)
        self.source_without_coding_box.grid(row=0, column=0, ipady=20)

        # output with coding
        self.output_with_coding_frame.grid(column=2, row=0, sticky="n")
        self.output_with_coding_title.grid(row=0, column=0, sticky="w")
        self.output_with_coding_box.grid(row=1, column=0)
        self.ber_with_coding_label.grid(row=2, column=0)
        self.source_with_coding_frame.grid(row=3, column=0, ipady=40)
        self.source_with_coding_box.grid(row=0, column=0, ipady=20)

        # TODO bmp_mode

        # bottom
        self.bottom_frame.grid(row=3, column=0)
        self.run_button.grid(row=0, column=0, pady=20)

    def key_release_input(self, val):
        self.source_bits = char_to_bin(self.input_box.get(1.0, END))
        self.change_text(self.source_box, self.source_bits)

    def key_release_probability(self, val):
        probability = self.probability_box.get(1.0, END)
        # remove unnecessary new line characters
        probability = probability.replace("\n", "")
        try:
            self.probability = convert_probability(probability)
            self.probability_box["bg"] = "white"
        except Exception as e:
            self.probability_box["bg"] = self.ERROR_COLOR

    def run(self):
        # without coding
        self.received_bits_without_coding = make_noise(self.source_bits, self.probability)
        text_without_coding = binary_to_string(self.received_bits_without_coding)
        self.change_text(self.source_without_coding_box, self.received_bits_without_coding)
        self.change_text(self.output_without_coding_box, text_without_coding)
        self.show_ber_without_coding()

        # with coding
        encoder = Encoder(self.source_bits)
        encoded_bits = encoder.encode()
        encoded_bits_with_noise = make_noise(encoded_bits, self.probability)
        decoder = Decoder(encoded_bits_with_noise, self.TRACEBACK_DEPTH)
        self.received_bits_with_coding = decoder.decode()
        text_with_coding = binary_to_string(self.received_bits_with_coding)
        self.change_text(self.source_with_coding_box, self.received_bits_with_coding)
        self.change_text(self.output_with_coding_box, text_with_coding)
        self.show_ber_with_coding()

    def change_text(self, widget, text):
        widget["state"] = NORMAL
        widget.delete(1.0, END)
        widget.insert(INSERT, text)
        widget["state"] = DISABLED

    def show_ber_without_coding(self):
        ber = count_ber(self.source_bits, self.received_bits_without_coding)
        self.ber_without_coding_label["text"] = "BER=" + str(ber)

    def show_ber_with_coding(self):
        ber = count_ber(self.source_bits, self.received_bits_with_coding)
        self.ber_with_coding_label["text"] = "BER=" + str(ber)


if __name__ == '__main__':
    root = Tk()
    app = App(root=root)
    app.mainloop()
