from tkinter import *
import tkinter as tk
from tkinter import Toplevel
from tkinter import Label
from tkinter import filedialog
from tkinter import messagebox
import threading
import inspect
import importlib
#import imp
import functools
from os import path

from PIL import Image, ImageTk


class ImageViewer:
    """
    :author: Sridhar Narayan
    :version: 1.1 - January 2015
    .. User code available in the drop down menu is automatically reloaded when invoked. Explicit reload only needed if a new function is added to file.
    .. Method show_message added
    .. 1.0 - October 2014

    :contact: narayans@uncw.edu
    :organization: University of North Carolina Wilmington

    :summary: Image viewer that supports display, modification, and saving of images in jpg, gif,
     png formats. User-written image processing functions can be loaded (added) into the viewer.
     These functions are then available for use as menu options. Multiple viewers can exist
     concurrently. An image displayed in *one* viewer can be accessed and modified by code invoked
     within the context of *any other* viewer.

    """
    __current_version = "1.1, January 2015"
    __viewerCount = 0
    __viewers = []
    __thisViewer = None
    __mainRoot = None
    __DEF_WIDTH = 640
    __DEF_HEIGHT = 480

    @staticmethod
    def get_viewer(viewer_id=None):
        """
        returns a reference to the ImageViewer instance identified by the viewer id. If no viewer id is specified, it returns a
        reference to the current, i.e. active, ImageViewer instance

        :param viewer_id: id of desired ImageViewer
        :return: reference to desired ImageViewer instance
        """

        if viewer_id is None or viewer_id == 0:  # called without a viewer id or id=0
            return ImageViewer.__thisViewer  # return a handle to this ImageViewer
        else:  # viewer id specified - returning corresponding viewer
            for v in ImageViewer.__viewers:
                if viewer_id == v.viewerId:
                    return v

        # No viewer exists with specified id
        return None

    def show_message(self, message):
        """
        Displays a user-specified message at the bottom of the viewer

        :param message: text of message to be displayed
        :return: None
        """
        self.__show_message(message)
        return None

    @staticmethod
    def __print_viewer_ids():
        for v in ImageViewer.__viewers:
            print(v)
            print(v.viewerId)

    def __init__(self):
        if ImageViewer.__viewerCount == 0:  # only for the initial (main) ImageViewer
            ImageViewer.__mainRoot = Tk()  # create root window
            self.root_window = self.__mainRoot
        else:
            self.root_window = Toplevel(ImageViewer.__mainRoot)

        #Disable resizing
        self.root_window.resizable(0, 0)

        # initialize instance attributes
        self.currentModule = None
        self.currentCodeFileName = None
        self.viewerId = ImageViewer.__viewerCount

        self.image = None
        self.pixel_array = None
        self.imageLabel = None
        #self.tasks = []

        self.statusLabel = ""
        self.currentModuleName = None

        # how often is the viewer updated
        self.updateInterval = 100

        self.opsMenu = None
        self.status = None

        self.__launch_viewer()

        ImageViewer.__viewerCount += 1

        # do this only for for the first viewer instance
        if ImageViewer.__viewerCount == 1:
            ImageViewer.__thisViewer = self  # it is the only viewer in existence
            self.__maybe_load_code()
            self.root_window.mainloop()

    # load the image manipulation code contained in the file from which the viewer was instantiated
    def __maybe_load_code(self):
        main_mod = sys.modules['__main__']
        self.currentModule = main_mod

        if hasattr(main_mod, '__file__'):  # launched by executing a Python script
            self.currentCodeFileName = path.abspath(sys.modules['__main__'].__file__)
            self.currentCodeFileName = self.currentCodeFileName.replace('\\', '/')
            self.__load_functions(main_mod, "Loaded ")

    @staticmethod
    def __create_extra_viewer():
        ImageViewer()

    def __update_default_viewer(self, event):
        ImageViewer.__thisViewer = self

    def __launch_viewer(self):
        self.__set_title("Image Viewer " + str(self.viewerId) + "  |")
        self.__add_menus()

        self.__reset_image(ImageViewer.__DEF_WIDTH, ImageViewer.__DEF_HEIGHT)
        self.__scheduled_viewer_update()
        ImageViewer.__viewers.append(self)

    def __show_message(self, msg):
        self.status.config(text=msg)

    def __print_location(self, event):
        if self.__image_exists():
            x = event.x
            y = event.y
            w = self.get_width()
            h = self.get_height()
            if x in range(w) and y in range(h):
                r, g, b = self.get_pixel(event.x, event.y)
                self.statusLabel = "(" + str(x) + "," + str(y) + ")=" + str(r) + "," + str(g) + "," + str(b)
                self.status.config(text=self.statusLabel)

    def __set_update_interval(self, interval):
        self.updateInterval = interval

    def __set_title(self, name):
        self.root_window.wm_title(name)

    def __add_menus(self):
        # create a toplevel menu
        menubar = Menu(self.root_window)

        # create a sub-menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.__init_image)
        filemenu.add_command(label="Open", command=self.__open_image_file)
        filemenu.add_command(label="Save", command=self.__save_image_file)
        filemenu.add_separator()

        filemenu.add_command(label="Viewer", command=self.__create_extra_viewer)
        filemenu.add_command(label="Exit", command=self.__exit_program)

        load_menu = Menu(menubar, tearoff=0)
        load_menu.add_command(label="Load", command=self.__load_code)
        load_menu.add_command(label="Reload", command=self.__reload_code)
        self.opsMenu = Menu(menubar, tearoff=0)

        # add sub-menus to menubar
        menubar.add_cascade(label="Image", menu=filemenu)
        menubar.add_cascade(label="MyCode", menu=load_menu)
        menubar.add_cascade(label="MyFuncs", menu=self.opsMenu)
        menubar.add_command(label="About", command=self.__show_about)

        self.status = Label(self.root_window, self.statusLabel, bd=1, relief=SUNKEN, anchor=W)
        self.status.pack(side=BOTTOM, fill=X)

        self.root_window.bind("<FocusIn>", self.__update_default_viewer)
        self.root_window.bind("<Enter>", self.__update_default_viewer)
        self.root_window.config(menu=menubar, width=ImageViewer.__DEF_WIDTH, height=ImageViewer.__DEF_HEIGHT)

    # load student code
    def __load_code(self):
        code_file_types = [("Python files", "*.py")]
        code_file_name = filedialog.askopenfilename(filetypes=code_file_types)
        if len(code_file_name) > 0:
            self.currentCodeFileName = code_file_name
            self.__load_file(code_file_name, "Loaded ")

    # reload the currently loaded code file
    def __reload_code(self):
        if self.currentCodeFileName is not None:
            # noinspection PyTypeChecker
            #self.__show_message("Reloaded code from " + self.currentCodeFileName)
            self.__load_file(self.currentCodeFileName, "Reloaded ")

    # open specified file and determine module
    def __load_file(self, code_file_name, message):
        folder, filename = code_file_name.rsplit('/', 1)
        if folder not in sys.path:
            sys.path.append(folder)
        module_name = filename.split('.')[0]
        self.currentModuleName = module_name

        module = importlib.import_module(module_name)
        #open_file, file_name, description = imp.find_module(module_name)
        #module = imp.load_module(code_file_name, open_file, file_name, description)

        self.__load_functions(module, message)

    # add functions defined in specified file to myOps menu
    def __load_functions(self, module, message):
        self.currentModule = module
        functions = inspect.getmembers(module, inspect.isfunction)

        current_menu_options = self.__menu_options(self.opsMenu)

        for f in functions:
            f_label = f[0]
            if f_label[0:2] == '__':
                continue  # skip over the 'private' functions
            f_name = f[1]
            # command associated with this menu option includes the function to be
            # executed as a part of the task as a parameter
            # functools.partial is necessary for this
            # since it allows a partially specified command to be set as the target of the menu action
            # duplicate labels not allowed
            if f_label in current_menu_options:  # delete option before updating
                index = current_menu_options.index(f_label)
                self.opsMenu.delete(index)
                current_menu_options.remove(f_label)

            # update existing option, or add new one
            self.opsMenu.add_command(label=f_label, command=functools.partial(self.__exec_task, f_name))

        self.__show_message(message+" code from " + module.__file__)

    # update the code binding (definition) for the specified function
    def __update_func_def(self, func_to_update):
        functions = inspect.getmembers(self.currentModule, inspect.isfunction)

        for f in functions:
            func_name = f[0]
            func_code = f[1]
            w_list = str(func_to_update).split()
            if func_name == w_list[1]:  # have we found the function def of interest?
                return func_code  # if so, return the current definition for that function

    # remove all options from specified menuItem
    @staticmethod
    def __clear_menu_options(menu_item):
        for i in range(menu_item.index(tk.END) + 1):
            menu_item.delete(i)

    # returns current list of labels under menu option opsMenu
    @staticmethod
    def __menu_options(menu_item):
        mx = menu_item.index(tk.END)
        if mx is None:
            return []
        else:
            return [menu_item.entrycget(i, 'label') for i in range(mx + 1)]

    # create and start a threaded task when called
    def __exec_task(self, f):
        self.__reload_code()  # reload the function definition file
        f = self.__update_func_def(f)  # update the binding of the function of interest
        func_name = str(f).split()[1] # get the name of the function
        self.show_message("Executing function: "+ func_name)
        threading.Thread(target=f).start()  # execute that function

    # scheduled update of viewer
    def __scheduled_viewer_update(self):
        self.__update_viewer()
        self.root_window.after(self.updateInterval, self.__scheduled_viewer_update)

    # update existing image
    def __update_viewer(self):
        if self.__image_exists():
            tkimage = ImageTk.PhotoImage(self.image)
            self.imageLabel.configure(image=tkimage)
            self.imageLabel.image = tkimage
            self.imageLabel.update_idletasks()

    def display_image(self, img):
        """
        Display the specified image in the referenced viewer instance

        :param img: reference to the image to be displayed
        :return: None
        """

        self.__display_image(img)
        return None

    def __display_image(self, im, filename=""):
        refresh_title = True
        if isinstance(im, __Picture__):
            im = im.im
            refresh_title = False

        self.image = im
        self.pixel_array = im.load()

        if self.__image_exists():
            self.__update_viewer()
        else:
            # Convert the Image object into a TkPhoto object
            tkimage = ImageTk.PhotoImage(self.image)

            self.imageLabel = Label(self.root_window, image=tkimage)
            self.imageLabel.image = tkimage
            self.imageLabel.bind("<B1-Motion>", self.__print_location)
            self.imageLabel.pack(side=TOP, fill=BOTH)

            #adjust window dimensions to current image dimensions
            w = tkimage.width()
            h = tkimage.height()
            self.root_window.config(width=w, height=h)

        if refresh_title:
            self.__update_title(im, filename)

    def __init_image(self):
        self.__reset_image(ImageViewer.__DEF_WIDTH, ImageViewer.__DEF_HEIGHT)

    def __reset_image(self, width, height):
        self.__display_image(self.__create_image(width, height))

    @staticmethod
    def blank_image(width, height):
        """
        returns a blank (white) image with the specified dimension

        :param width: width of the desired image (like 320)
        :param height: height of the desired image (like 240)
        :return: blank (white) image with the specified dimensions
        """
        return __Picture__(width, height)

    @staticmethod
    def __create_image(width=320, height=240):
        im = Image.new("RGB", (width, height), "yellow")
        return im

    def get_width(self):
        """
        return the width of the image visible in the referenced viewer instance

        :return: the width of the image visible in the referenced viewer instance
        """
        if self.__image_exists():
            return self.image.size[0]
        else:
            return 0

    def get_height(self):
        """
        return the height of the image visible in the referenced viewer instance

        :return: the height of the image visible in the referenced viewer instance
        """
        if self.__image_exists():
            return self.image.size[1]
        else:
            return 0

    # return an array-like data structure of r,g,b triples corresponding to all the pixels in the image
    # changes to this data structure are reflected in image immediately
    def __get_rgb(self):
        if self.__image_exists():
            return self.pixel_array

    #assign RGB values to all pixels in current image
    def __set_rgb(self, pixels):
        if self.__image_exists():
            self.pixel_array = pixels
            self.__update_viewer()

    def get_pixel(self, x, y):
        """
        return a r,g,b-triple corresponding to the red,green,blue intensities of pixel at
        specified location (x,y) within the referenced viewer instance

        :param x: the x coordinate of a location in the image
        :param y: the y coordinate of a location in the image
        :return: a triple corresponding to the red, green, blue intensities of the pixel at the specified (x,y) location within the referenced viewer instance
        """
        if self.__image_exists():
            return self.pixel_array[x, y]
        else:
            return None

    def set_pixel(self, x, y, r, g, b):
        """
        assign r,g,b values to pixel at specified location (x,y) within the referenced viewer instance

        :param x: the x coordinate of a location within the referenced viewer instance
        :param y: the y coordinate of a location within the referenced viewer instance
        :param r: the red intensity of that pixel (0..255)
        :param g: the green intensity of that pixel (0..255)
        :param b: the blue intensity of that pixel (0..255)
        :return: None
        """
        if self.__image_exists():
            self.pixel_array[x, y] = (r, g, b)

    #returns True if an image is already visible in the viewer, False otherwise
    def __image_exists(self):
        return self.imageLabel is not None

    def __open_image_file(self):
        #Use a file browser to open and display an image file

        image_file_types = [("Image Files", "*.jpg;*.gif;*.png;"),
                            ("JPEG", '*.jpg'),
                            ("PNG", '*.png'),
                            ("GIF", '*.gif'),
                            ('All', '*')]
        image_file_name = filedialog.askopenfilename(filetypes=image_file_types)
        if len(image_file_name) > 0:
            im = Image.open(image_file_name)
            im = im.convert("RGB")
            self.__display_image(im, image_file_name)

    def __update_title(self, im, image_file_name):
        s = self.root_window.title()
        self.__set_title(s[0:s.index('|') + 1] + str(im.size[0]) + "x" + str(im.size[1]) + " | " +
                         str(im.format) + " | " + image_file_name)

    #Save the current image in a user-specified file
    def __save_image_file(self):
        #Use a file browser to save displayed image file
        image_file_types = [("Image Files", "*.jpg;*.gif;*.png;"),
                            ("JPEG", '*.jpg'),
                            ("PNG", '*.png'),
                            ("GIF", '*.gif'),
                            ('All', '*')]
        image_file_name = filedialog.asksaveasfilename(filetypes=image_file_types)
        if len(image_file_name) > 0:
            self.image.save(image_file_name)

    def __exit_program(self):
        self.root_window.destroy()

    def __show_about(self):
        #tkMessageBox.function(title, message [, options]).
        msg = "Project SIMPLE is\nSimplified Image Processing (in Python, for) Learning Enhancement"
        messagebox.showinfo(title = "About SIMPLE", message = msg+"\nversion "+self.__current_version+
                            "\nSridhar Narayan\nnarayans@uncw.edu\nUniversity of North Carolina Wilmington")


if __name__ == '__main__':
    ImageViewer()


# Picture class uses the PIL Image class and adds get_height, get_width, get_pixel, set_pixel etc. to maintain consistency
# with the ImageViewer interface
class __Picture__:
    def __init__(self, width, height):
        self.im = Image.new("RGB", (width, height), "white")
        self.pixel_array = self.im.load()
        self.size = self.im.size
        self.name = ""

    def load(self):
        return self.im.load()

    def get_height(self):
        return self.im.size[1]

    def get_width(self):
        return self.im.size[0]

    def get_pixel(self, x, y):
        return self.pixel_array[x, y]

    def set_pixel(self, x, y, r, g, b):
        self.pixel_array[x, y] = (r, g, b)
