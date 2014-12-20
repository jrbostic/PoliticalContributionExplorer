from Tkinter import *
import db_manager

__author__ = 'jessebostic'

class DisplayWindow:

    def __init__(self):
        self.root = Tk()
        self.root.resizable(0, 0)

        self.inner_window = Frame(self.root)
        self.inner_window.pack()

        self.entry = Entry(self.inner_window)
        self.entry.grid(column=0, row=0, sticky=NSEW)

        self.button = Button(self.inner_window, text="FIND CONTRIBUTOR", command=self.create_selection_window)
        self.button.grid(column=1, row=0, sticky=NSEW)

        self.canvas = Canvas(self.root, width=800, height=500)
        self.canvas.pack()

        self.select_list = None
        self.selected_contributor = None
        self.contributor = None
        self.contributions = None
        self.lobbies = None

        #self.render_display()

        self.root.mainloop()

    def render_display(self):

        self.canvas.delete('all')

        if self.selected_contributor is not None:

            ratio = 1
            if self.contributor[1] != 0 != self.contributor[2]:
                ratio = self.contributor[1]/(self.contributor[1]+self.contributor[2])

            contribution_percent = ratio*100
            contribution_slice = ratio*359.999
            lobby_slice = -359.999 + contribution_slice

            if contribution_slice > 0.01:
                self.canvas.create_arc(self.root.winfo_width()/2-50, self.root.winfo_height()/2-50,
                                       self.root.winfo_width()/2+50, self.root.winfo_height()/2+50,
                                       start=0, extent=contribution_slice, fill='blue',
                                       activefill='green', outline='white', activeoutline='black', style=PIESLICE)
                self.canvas.create_text(self.root.winfo_width()/2+26, self.root.winfo_height()/2-5,
                                        text='{:.1f}%'.format(contribution_percent), fill='blue')

            if lobby_slice < -0.01:
                self.canvas.create_arc(self.root.winfo_width()/2-50, self.root.winfo_height()/2-50,
                                       self.root.winfo_width()/2+50, self.root.winfo_height()/2+50,
                                       start=0, extent=lobby_slice, fill='red',
                                       activefill='green', outline='white', activeoutline='black', style=PIESLICE)
                self.canvas.create_text(self.root.winfo_width()/2+26, self.root.winfo_height()/2+10,
                                        text='{:.1f}%'.format(100-contribution_percent), fill='red')

            self.canvas.create_text(self.root.winfo_width()/2, self.root.winfo_height()/4,
                                    text=self.selected_contributor)
            self.canvas.create_text(self.root.winfo_width()/2, self.root.winfo_height()/4+20,
                                    text='Total: ${:,.2f}'.format(self.contributor[1]+self.contributor[2]))
            self.canvas.create_text(self.root.winfo_width()/5, self.root.winfo_height()/5,
                                    text='Contributions: ${:,.2f}'.format(self.contributor[1]))

            listbox1 = Listbox(self.canvas, width=30, height=20)
            listbox1.place(relx=.05, rely=.25)
            for entry in self.contributions:
                listbox1.insert(END, entry[0])

            self.canvas.create_text((self.root.winfo_width()/5)*4, self.root.winfo_height()/5,
                                    text='Lobbies: ${:,.2f}'.format(self.contributor[2]))

            listbox2 = Listbox(self.canvas, width=30, height=20)
            listbox2.place(relx=.65, rely=.25)
            for entry in self.lobbies:
                listbox2.insert(END, entry[0])

        #self.canvas.after(100, self.render_display)

    def create_selection_window(self):

        def set_selection(select_list):
            self.selected_contributor = select_list.get(select_list.curselection())
            self.contributor = db_manager.get_contributor(self.selected_contributor)
            self.contributions = db_manager.get_contributions(self.selected_contributor)
            self.lobbies = db_manager.get_lobbies(self.selected_contributor)

            self.render_display()

            print self.contributor
            print self.contributions
            print self.lobbies

            scroll_window.destroy()

        results = db_manager.get_contributor_names(self.entry.get())

        scroll_window = Toplevel(self.root)
        scroll_window.geometry("%dx%d%+d%+d" % (500, 200, self.canvas.winfo_rootx()+10, self.canvas.winfo_rooty()))

        inner_window = Frame(scroll_window)
        inner_window.pack(fill=BOTH)

        scrollbar = Scrollbar(inner_window, orient=VERTICAL)
        xscrollbar = Scrollbar(inner_window, orient=HORIZONTAL)
        self.select_list = Listbox(inner_window, yscrollcommand=scrollbar.set, xscrollcommand=xscrollbar.set)
        scrollbar.config(command=self.select_list.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        xscrollbar.config(command=self.select_list.xview)
        xscrollbar.pack(side=BOTTOM, fill=X)
        for item in results:
            self.select_list.insert(END, item)
        self.select_list.pack(side=LEFT, fill=BOTH, expand=1)

        #currently destroy window... need to return/set selection
        Button(scroll_window, text="Select", command=lambda sel=self.select_list: set_selection(sel)).pack(side=LEFT, expand=1)
        Button(scroll_window, text="Cancel", command=scroll_window.destroy).pack(side=RIGHT, expand=1)

if __name__ == "__main__":
    DisplayWindow()