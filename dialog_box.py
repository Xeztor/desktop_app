import tkinter as tk
from helpers import AvailableList, raise_app
from event_queue import threads_event_queue
from event import EVENT
from ctypes import windll

user32 = windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)


class DialogBox:
    def __init__(self):
        self.notification_level = 0
        self.exit_event = EVENT

        self.root = tk.Tk()
        self.root.title("Cards Available")
        self.root.geometry(f"530x400+{screen_width - 540}+420")
        self.root.iconbitmap('caseking.ico')

        # CaseKing Available list
        self.available_list_caseking = AvailableList(self.root)
        self.show_caseking_box()

        # Mindfactory Available list
        self.available_list_mindfactory = AvailableList(self.root)
        self.show_mindfactory_box()

        self.notification_level_listener()
        self.check_queue_loop()

        self.root.mainloop()

    def notification_level_listener(self):
        if not threads_event_queue.empty():
            queue_item = threads_event_queue.get_nowait()
            if 'notifiaction_level' in queue_item:
                level = int(queue_item.split('=')[1])
                self.notification_level = level
            else:
                threads_event_queue.put(queue_item)

        self.root.after(1000, self.notification_level_listener)

    def check_queue_loop(self):
        try:
            queue_item = threads_event_queue.get_nowait()
            if queue_item == 'dialog_stop':
                self.root.destroy()
            elif isinstance(queue_item, list):
                self.cards_available_handler(queue_item)
            else:
                threads_event_queue.put(queue_item)
        except:
            # print('dialog_box: trying again') # For Debug
            pass

        self.root.after(1000, self.check_queue_loop)

    def cards_available_handler(self, queue_item: list):
        signature = queue_item.pop()
        if self.notification_level:
            if len(queue_item) >= self.notification_level:
                raise_app(root=self.root)
        self.update_available(queue_item, signature)

    def update_available(self, queue_item: list, signature: str):
        if signature == 'caseking':
            self.update_available_caseking_list(queue_item)
            self.show_mindfactory_box()
        elif signature == 'mindfactory':
            self.update_available_mindfactory_list(queue_item)
            self.show_mindfactory_box()

    def update_available_caseking_list(self, queue_item):
        self.available_list_caseking.update(queue_item)
        self.show_caseking_box()

    def update_available_mindfactory_list(self, queue_item):
        self.available_list_mindfactory.update(queue_item)
        self.show_mindfactory_box()

    def show_caseking_box(self):
        self.caseking_cards_label = tk.Label(self.root, text="Cards available in Caseking: ", font='arial 12')
        self.caseking_cards_label.grid(row=0, column=0, padx=10, sticky='w')
        self.available_list_caseking.show(1)

    def show_mindfactory_box(self):
        if self.available_list_caseking.models_labels_list:
            row = self.get_last_caseking_label_row()
        else:
            row = 0

        self.mindfactory_cards_label = tk.Label(self.root, text="Cards available in Mindfactory: ", font='arial 12')
        self.mindfactory_cards_label.grid(row=row + 1, column=0, padx=10, sticky='w')
        self.available_list_mindfactory.show(row + 2)

    def get_last_caseking_label_row(self):
        return self.available_list_caseking.models_labels_list[-1].grid_info()['row']


if __name__ == '__main__':
    DialogBox()
