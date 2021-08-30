from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from source_generator import char_to_bin, get_bmp_data
from noise_generator import make_noise, convert_probability
from encoder import Encoder
from receiver import binary_to_string, count_ber, bin_to_bmp
from decoder import Decoder
import threading

from PIL import ImageTk, Image


def change_text(widget, text):
    widget["state"] = NORMAL
    widget.delete(1.0, END)
    widget.insert(INSERT, text)
    widget["state"] = DISABLED


class App(Frame):
    SIZE = "1200x720"
    ERROR_COLOR = "#e57373"
    TRACEBACK_DEPTH = 30
    IMAGE_WIDTH = 384
    IMAGE_HEIGHT = 256

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
        self.probability = ""
        self.received_bits_without_coding = ""
        self.received_bits_with_coding = ""
        self.active_mode = "text"
        self.image_filename = "./sample.bmp"
        self.create_widgets()
        self.build()

    def create_widgets(self):
        # top
        self.create_top_widget()

        # text_mode
        if self.active_mode == "text":
            self.create_text_mode_widget()

        # bmp_mode
        elif self.active_mode == "bmp":
            self.create_bmp_mode_widget()

        # bottom
        self.create_bottom_widget()

    def create_top_widget(self):
        self.top_frame = Frame(self.root,
                               pady=20,
                               )
        self.top_frame.columnconfigure(0, weight=1)

        self.change_mode_button = Button(self.top_frame,
                                         text="change mode",
                                         pady=4,
                                         height=1,
                                         width=60,
                                         anchor=CENTER,
                                         command=self.change_mode
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

    def create_text_mode_widget(self):
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

    def create_bmp_mode_widget(self):
        self.bmp_mode_frame = Frame(self.root,
                                    )
        self.bmp_mode_frame.columnconfigure(0, weight=1)
        self.bmp_mode_frame.columnconfigure(1, weight=1)
        self.bmp_mode_frame.columnconfigure(2, weight=1)

        self.select_file_button = Button(self.bmp_mode_frame,
                                         text="select BMP file",
                                         command=self.open_file
                                         )
        input_output_width = 40
        self.input_frame = Frame(self.bmp_mode_frame)
        self.input_title = Label(self.input_frame,
                                 text="Input:",
                                 anchor=W,
                                 width=input_output_width
                                 )
        self.input_image = Label(self.input_frame,
                                 )
        self.input_ber_label = Label(self.input_frame,
                                     text="BER=0"
                                     )

        self.output_without_coding_frame = Frame(self.bmp_mode_frame)
        self.output_without_coding_title = Label(self.output_without_coding_frame,
                                                 text="output without coding:",
                                                 anchor=W,
                                                 width=input_output_width
                                                 )
        self.output_without_coding_image = Label(self.output_without_coding_frame,
                                                 )
        self.ber_without_coding_label = Label(self.output_without_coding_frame,
                                              text="BER=0"
                                              )

        self.output_with_coding_frame = Frame(self.bmp_mode_frame)
        self.output_with_coding_title = Label(self.output_with_coding_frame,
                                              text="Output with coding:",
                                              anchor=W,
                                              width=input_output_width
                                              )
        self.output_with_coding_image = Label(self.output_with_coding_frame,
                                              )
        self.ber_with_coding_label = Label(self.output_with_coding_frame,
                                           text="BER=0"
                                           )

    def create_bottom_widget(self):
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
        if self.active_mode == "text":
            self.build_text_mode()
            self.change_mode_button["text"] = "Change to BMP mode"

        # bmp_mode
        elif self.active_mode == "bmp":
            self.build_bmp_mode()
            self.change_mode_button["text"] = "Change to text mode"

        # bottom
        self.bottom_frame.grid(row=3, column=0)
        self.run_button.grid(row=0, column=0, pady=20)

    def build_text_mode(self):
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

    def build_bmp_mode(self):
        self.bmp_mode_frame.grid(row=2, column=0, padx=24, sticky="nwse")
        self.select_file_button.grid(row=0, column=0, sticky="w", pady=20)

        self.input_frame.grid(row=1, column=0)
        self.input_title.grid(row=0, column=0)
        self.input_image.grid(row=1, column=0)
        self.set_input_image()
        self.input_ber_label.grid(row=2, column=0)

        self.output_without_coding_frame.grid(row=1, column=1, padx=20)
        self.output_without_coding_title.grid(row=0, column=0)
        self.output_without_coding_image.grid(row=1, column=0)
        self.set_output_image_without_coding("null.png")
        self.ber_with_coding_label.grid(row=2, column=0)

        self.output_with_coding_frame.grid(row=1, column=2)
        self.output_with_coding_title.grid(row=0, column=0)
        self.output_with_coding_image.grid(row=1, column=0)
        self.set_output_image_with_coding("null.png")
        self.ber_without_coding_label.grid(row=2, column=0)

    def key_release_input(self, val):
        self.source_bits = char_to_bin(self.input_box.get(1.0, END))
        change_text(self.source_box, self.source_bits)

    # count probability everytime text has been changed
    def key_release_probability(self, val):
        probability = self.probability_box.get(1.0, END)
        # remove unnecessary new line characters
        probability = probability.replace("\n", "")
        try:
            self.probability = convert_probability(probability)
            self.probability_box["bg"] = "white"
        except Exception as e:
            self.probability_box["bg"] = self.ERROR_COLOR

    # actions after pressing run button
    def run(self):
        if self.active_mode == "text":
            # without coding
            self.received_bits_without_coding = make_noise(self.source_bits, self.probability)
            text_without_coding = binary_to_string(self.received_bits_without_coding)
            change_text(self.source_without_coding_box, self.received_bits_without_coding)
            change_text(self.output_without_coding_box, text_without_coding)
            self.show_ber_without_coding()

            # with coding
            encoder = Encoder(self.source_bits)
            encoded_bits = encoder.encode()
            encoded_bits_with_noise = make_noise(encoded_bits, self.probability)
            decoder = Decoder(encoded_bits_with_noise, self.TRACEBACK_DEPTH)
            self.decode_text_thread = threading.Thread(target=self.decode_text, args=(decoder,))
            self.decode_text_thread.start()
        elif self.active_mode == "bmp":
            self.source_bits = get_bmp_data(self.image_filename)
            self.without_coding_thread = threading.Thread(target=self.make_image_without_coding)
            self.with_coding_thread = threading.Thread(target=self.make_image_with_coding)
            self.without_coding_thread.start()
            self.with_coding_thread.start()

    def decode_text(self, decoder):
        self.run_button_disable()
        self.received_bits_with_coding = decoder.decode()
        text_with_coding = binary_to_string(self.received_bits_with_coding)
        change_text(self.source_with_coding_box, self.received_bits_with_coding)
        change_text(self.output_with_coding_box, text_with_coding)
        self.show_ber_with_coding()
        self.run_button_enable()

    def show_ber_without_coding(self):
        ber = count_ber(self.source_bits, self.received_bits_without_coding)
        self.ber_without_coding_label["text"] = "BER=" + str(ber)

    def show_ber_with_coding(self):
        ber = count_ber(self.source_bits, self.received_bits_with_coding)
        self.ber_with_coding_label["text"] = "BER=" + str(ber)

    def run_button_disable(self):
        self.run_button["state"] = DISABLED
        self.run_button["text"] = "COUNTING..."

    def run_button_enable(self):
        self.run_button["state"] = NORMAL
        self.run_button["text"] = "RUN"

    def select_file_button_disable(self):
        self.select_file_button["state"] = DISABLED

    def select_file_button_enable(self):
        self.select_file_button["state"] = NORMAL

    def change_mode(self):
        if self.active_mode == "text":
            self.active_mode = "bmp"
            self.text_mode_frame.destroy()
            self.create_bmp_mode_widget()
            self.build_bmp_mode()
            self.change_mode_button["text"] = "Change to text mode"
        elif self.active_mode == "bmp":
            self.active_mode = "text"
            self.bmp_mode_frame.destroy()
            self.create_text_mode_widget()
            self.build_text_mode()
            self.change_mode_button["text"] = "Change to BMP mode"

    # Open file then change input image
    def open_file(self):
        try:
            self.image_filename = filedialog.askopenfilename(filetypes=[("BMP file format", "*.bmp")],
                                                             initialdir='./'
                                                             )
            self.set_input_image()
        except AttributeError as e:
            print(e)

    def set_input_image(self):
        image = Image.open(self.image_filename)
        image = image.resize((self.IMAGE_WIDTH, self.IMAGE_HEIGHT))
        image = ImageTk.PhotoImage(image)
        self.input_image["image"] = image
        self.input_image.image = image

    def set_output_image_without_coding(self, path):
        image = Image.open(path)
        image = image.resize((self.IMAGE_WIDTH, self.IMAGE_HEIGHT))
        image = ImageTk.PhotoImage(image)
        self.output_without_coding_image["image"] = image
        self.output_without_coding_image.image = image

    # Count everything and show received image without coding
    def make_image_without_coding(self):
        # disable buttons
        self.run_button_disable()
        self.select_file_button_disable()

        self.received_bits_without_coding = make_noise(self.source_bits, self.probability)
        bin_to_bmp(self.received_bits_without_coding, r"without_coding.bmp", self.image_filename)

        # Try change image if new is openable
        try:
            self.set_output_image_without_coding("without_coding.bmp")
        except Exception as e:
            self.set_output_image_without_coding("null.png")
        self.show_ber_without_coding()

        # if other thread ends enable buttons
        if not self.with_coding_thread.is_alive():
            self.run_button_enable()
            self.select_file_button_enable()

    def set_output_image_with_coding(self, path):
        image = Image.open(path)
        image = image.resize((self.IMAGE_WIDTH, self.IMAGE_HEIGHT))
        image = ImageTk.PhotoImage(image)
        self.output_with_coding_image["image"] = image
        self.output_with_coding_image.image = image

    # Do all maths and show received image with coding
    def make_image_with_coding(self):
        # disable buttons
        self.run_button_disable()
        self.select_file_button_disable()

        encoder = Encoder(self.source_bits)
        source_data = encoder.encode()
        received_data = make_noise(source_data, self.probability)
        decoder = Decoder(received_data, self.TRACEBACK_DEPTH)
        self.received_bits_with_coding = decoder.decode()
        bin_to_bmp(self.received_bits_with_coding, r"with_coding.bmp", self.image_filename)

        # Try change image if new is openable
        try:
            self.set_output_image_with_coding("with_coding.bmp")
        except Exception as e:
            self.set_output_image_with_coding("null.png")

        # if other thread ends enable buttons
        self.show_ber_with_coding()

        if not self.without_coding_thread.is_alive():
            self.run_button_enable()
            self.select_file_button_enable()


if __name__ == '__main__':
    root = Tk()
    app = App(root=root)
    app.mainloop()
