"""Provides GUI for exploring political influence database."""

from Tkinter import *
import os
import db_manager
import re
__author__ = 'jessebostic'

class DisplayWindow:
    """Class providing a graphical interface for exploring specific contributor
    records residing in political influence database.
    """

    def __init__(self):
        """Sets up tkinter components, geometry managers, bindings, and instance-level members.

        :return: new DisplayWindow instance
        """

        # master widget
        self.root = Tk()
        self.root.resizable(0, 0)
        self.root.title("Political Influence Explorer")

        # frame for upper entry box and search button
        self.inner_window = Frame(self.root)
        self.inner_window.pack()

        # setup input box for search
        self.entry = Entry(self.inner_window)
        self.entry.grid(column=0, row=0, sticky=NSEW)
        self.entry.bind('<Return>', self.create_selection_window)
        self.entry.focus_set()

        # setup year selection box
        self.year_options = self.get_available_years()
        self.year_var = StringVar(self.inner_window)
        self.year_var.set(self.year_options[0])
        self.year_option_menu = apply(OptionMenu, (self.inner_window, self.year_var) + self.year_options)
        self.year_option_menu.grid(column=1, row=0, sticky=NSEW)

        # setup search button
        self.button = Button(self.inner_window, text="FIND CONTRIBUTOR", command=self.create_selection_window)
        self.button.grid(column=2, row=0, sticky=NSEW)

        # canvas for drawing data rep
        self.canvas = Canvas(self.root, width=800, height=500)
        self.canvas.pack()

        # various members for tracking current selection
        self.select_list = None
        self.selected_contributor = None
        self.recipient_listbox = None
        self.contributor = None
        self.contributions = None
        self.lobbies = None

        self.root.mainloop()

    def render_display(self):
        """Updates all graphical contents of canvas.  Uses clunky placement calculations which could/should
        be simplified and refactored on next iteration.
         """

        self.canvas.delete('all')

        if self.selected_contributor is not None:

            # get ratio of contribution/(contribution+lobby)
            #  avoiding division by zero
            ratio = 0
            if self.contributor[1] != 0 or self.contributor[2] != 0:
                ratio = self.contributor[1]/(self.contributor[1]+self.contributor[2])

            # extract pie degrees from ratio
            contribution_percent = ratio*100
            contribution_slice = ratio*359.999
            lobby_slice = -359.999 + contribution_slice

            # create pie slices in center of window
            if contribution_slice > 0.001:
                self.canvas.create_arc(self.root.winfo_width()/2-50, self.root.winfo_height()/2-50,
                                       self.root.winfo_width()/2+50, self.root.winfo_height()/2+50,
                                       start=0, extent=contribution_slice, fill='blue',
                                       activefill='green', outline='white', activeoutline='black', style=PIESLICE)
                self.canvas.create_text(self.root.winfo_width()/2+26, self.root.winfo_height()/2-5,
                                        text='{:.1f}%'.format(contribution_percent), fill='blue')

            if lobby_slice < -0.001:
                self.canvas.create_arc(self.root.winfo_width()/2-50, self.root.winfo_height()/2-50,
                                       self.root.winfo_width()/2+50, self.root.winfo_height()/2+50,
                                       start=0, extent=lobby_slice, fill='red',
                                       activefill='green', outline='white', activeoutline='black', style=PIESLICE)
                self.canvas.create_text(self.root.winfo_width()/2+26, self.root.winfo_height()/2+10,
                                        text='{:.1f}%'.format(100-contribution_percent), fill='red')

            # non-piechart display elements in center of window
            self.canvas.create_text(self.root.winfo_width()/2, self.root.winfo_height()/10,
                                    text=self.selected_contributor)
            self.canvas.create_text(self.root.winfo_width()/2, self.root.winfo_height()/10+20,
                                    text='Total: ${:,.2f}'.format(self.contributor[1]+self.contributor[2]))
            self.canvas.create_rectangle((self.root.winfo_width()/10)*4, (self.root.winfo_height()/10)*7,
                                        (self.root.winfo_width()/10)*4+20, (self.root.winfo_height()/10)*7+15,
                                         fill='blue')
            self.canvas.create_text((self.root.winfo_width()/10)*5, (self.root.winfo_height()/10)*7+8,
                                    text='Contributions')
            self.canvas.create_rectangle((self.root.winfo_width()/10)*4, (self.root.winfo_height()/10)*7.5,
                                        (self.root.winfo_width()/10)*4+20, (self.root.winfo_height()/10)*7.5+15,
                                         fill='red')
            self.canvas.create_text((self.root.winfo_width()/10)*5, (self.root.winfo_height()/10)*7.5+8, text='Lobbies')

            # contributions arrangement at left of window
            self.canvas.create_text(self.root.winfo_width()/5, self.root.winfo_height()/5,
                                    text='Contributions: ${:,.2f}'.format(self.contributor[1]))
            self.recipient_listbox = Listbox(self.canvas, width=30, height=20)
            self.recipient_listbox.place(relx=.05, rely=.25)
            for entry in self.contributions:
                self.recipient_listbox.insert(END, entry[0])
            self.recipient_listbox.bind("<Double-Button-1>", self.show_recipient)

            # lobbies arrangement at right of window
            self.canvas.create_text((self.root.winfo_width()/5)*4, self.root.winfo_height()/5,
                                    text='Lobbies: ${:,.2f}'.format(self.contributor[2]))
            agency_listbox = Listbox(self.canvas, width=30, height=20)
            agency_listbox.place(relx=.65, rely=.25)
            for entry in self.lobbies:
                agency_listbox.insert(END, entry[0])

    def show_recipient(self, event=None):
        """Shows small popup window with recipient name and specific contribution amount.

        :param event: allows key-bound callbacks (not used in function)
        """

        # set up window and geometry
        recipient_window = Toplevel(self.recipient_listbox)
        recipient_window.title("Contribution Detail")

        x = self.recipient_listbox.winfo_rootx()+10
        y = self.recipient_listbox.winfo_rooty()/5
        height = self.recipient_listbox.winfo_height()
        geom = "%dx%d+%d+%d" % (300, 100, x,y+height)
        recipient_window.geometry(geom)

        # retrieve and insert data particulars
        recipient_name = self.recipient_listbox.get(self.recipient_listbox.curselection())
        recipient_tuple = None
        for entry in self.contributions:
            if recipient_name == entry[0]:
                recipient_tuple = entry
        Label(recipient_window, text='{}'.format(recipient_tuple[0])).pack()
        Label(recipient_window, text='${:,.2f}'.format(recipient_tuple[1])).pack()

    def create_selection_window(self, event=None):
        """Initializes display window for contributor selection based on text in main entry widget.

        :param event: allows key-bound callbacks (not used in function)
        """

        def set_selection(select_list):
            """If an item has been selected in Listbox, sets DisplayWindow instance fields to appropriate values,
            fires off graphical display repaint, and destroys selection window.

            :param select_list: contributor Listbox to get user selection from
            """

            if select_list.curselection() != ():

                year_selected = self.year_var.get()

                self.selected_contributor = select_list.get(select_list.curselection())
                self.contributor = db_manager.get_contributor(self.selected_contributor, year_selected)
                self.contributions = db_manager.get_contributions(self.selected_contributor, year_selected)
                self.lobbies = db_manager.get_lobbies(self.selected_contributor, year_selected)

                self.render_display()
                scroll_window.destroy()

        results = db_manager.get_contributor_names(self.entry.get(), self.year_var.get())

        # creates selection window along with x and y scroll bars
        scroll_window = Toplevel(self.root)
        scroll_window.geometry('%dx%d%+d%+d' % (500, 200, self.canvas.winfo_rootx()+10, self.canvas.winfo_rooty()))
        scroll_window.title('Select Contributor')

        inner_window = Frame(scroll_window)
        inner_window.pack(fill=BOTH)

        scrollbar = Scrollbar(inner_window, orient=VERTICAL)
        xscrollbar = Scrollbar(inner_window, orient=HORIZONTAL)
        self.select_list = Listbox(inner_window, yscrollcommand=scrollbar.set, xscrollcommand=xscrollbar.set)
        scrollbar.config(command=self.select_list.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        xscrollbar.config(command=self.select_list.xview)
        xscrollbar.pack(side=BOTTOM, fill=X)

        # populate contributors into listbox
        for item in results:
            self.select_list.insert(END, item)
        self.select_list.pack(side=LEFT, fill=BOTH, expand=1)

        Button(scroll_window, text="Select",
               command=lambda sel=self.select_list: set_selection(sel)).pack(side=LEFT, expand=1)
        Button(scroll_window, text="Cancel", command=scroll_window.destroy).pack(side=RIGHT, expand=1)

    def get_available_years(self):
        matcher = re.compile('^influence(\d{4}).db$')
        local_files = os.listdir(os.curdir)
        valid_dbs = []
        for file in local_files:
            data_year = matcher.findall(file)
            if len(data_year):
                valid_dbs.append(data_year[0])
        return tuple(sorted(valid_dbs))

if __name__ == "__main__":
    DisplayWindow()