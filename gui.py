import tkinter as tk
from helpers import get_vga_options, get_selected, AskedList, raise_app
from bot_thread import bot_thread
from threading import Thread
import json
from event import EVENT
from event_queue import threads_event_queue
from ctypes import windll

user32 = windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)


class GUI:
    def __init__(self, root):
        self.exit_event = EVENT

        self.root = root
        self.root.title("Case King Bot")
        self.root.geometry(f"420x420+{screen_width - 430}+0")
        self.root.iconbitmap('caseking.ico')

        # Grid all options
        self.nvidia_lab = tk.Label(self.root, text="Nvidia", font='arial 14', anchor='center')
        self.nvidia_lab.grid(row=0, column=0, padx=10)
        self.nvidia_options = get_vga_options(self.root, 'nvidia')
        self.show_options(self.nvidia_options, row=1, col=0)

        self.amd_lab = tk.Label(self.root, text="AMD", font='arial 14', anchor='center')
        self.amd_lab.grid(row=0, column=1, padx=10)
        self.amd_options = get_vga_options(self.root, 'amd')
        self.show_options(self.amd_options, row=1, col=1)

        # Apply Button
        self.apply_btn = tk.Button(self.root, text="Apply", font='arial 10',
                                   command=lambda: self.apply(self.nvidia_options, self.amd_options))
        self.apply_btn.grid(row=0, rowspan=2, column=3, padx=10, sticky='ew')

        # Start bot button
        self.start_btn = tk.Button(self.root, text="Start", font='arial 10', command=self.start_bot)
        self.start_btn.grid(row=2, rowspan=2, column=3, padx=10, sticky='ew')

        # Stop bot button
        self.stop_btn = tk.Button(self.root, text="Stop", font='arial 10', command=self.stop_bot_btn, state=tk.DISABLED)
        self.stop_btn.grid(row=4, rowspan=2, column=3, padx=10, sticky='ew')

        # Bot state label
        self.bot_state = tk.Label(self.root, text="Bot is now stopped.", font='arial 10', anchor='center')
        self.bot_state.grid(row=6, rowspan=2, column=3, padx=10)

        # Notification CheckButton
        self.notification_int = tk.IntVar()
        self.notification_checkbtn = tk.Checkbutton(
            self.root,
            compound="right",
            text='Notify me.',
            font="arial 10",
            offvalue=0,
            onvalue=3,
            variable=self.notification_int, )
        self.notification_checkbtn.grid(row=8, rowspan=2, column=3, padx=10)
        self.notification_checkbtn.select()
        # Apply notification settings Button
        self.apply_notification_btn = tk.Button(self.root, text='Apply notification settings.', font='arial 10',
                                                command=self.apply_notification_settings)
        self.apply_notification_btn.grid(row=10, rowspan=2, column=3, padx=10, sticky='ew')

        # Show asked models
        self.now_selected_lab = tk.Label(self.root, text='Now Selected: ', font='arial 10')
        self.last_used_row_col0 = self.nvidia_options[-1].grid_info()['row']
        self.now_selected_lab.grid(row=self.last_used_row_col0 + 1, column=0, padx=10, sticky='w')

        self.asked_list = AskedList(root, self.last_used_row_col0 + 2)
        self.asked_list.show()

        self.root.columnconfigure(3, weight=2)
        # self.root.grid_columnconfigure(3, minsize=100)

    def apply(self, nvidia_opts, amd_opts):
        nvidia_selected = get_selected(nvidia_opts)
        amd_selected = get_selected(amd_opts)
        all_selected = {
            'amd': amd_selected,
            'nvidia': nvidia_selected,
        }
        with open('asked.txt', 'w') as file:
            json.dump(all_selected, file)

        self.asked_list.update()

    def apply_notification_settings(self):
        threads_event_queue.put(f'notifiaction_level={self.notification_int.get()}')

    def start_bot(self):
        self.exit_event.clear()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.start_bot_thread()
        self.bot_state.config(text='Bot is now running.')
        self.is_bot_stopped_listener()
        self.apply_notification_settings()

    def stop_bot_btn(self):
        self.exit_event.set()
        self.bot_state.config(text='Bot is now stopping...\nPlease wait.')

    def stop_bot(self):
        threads_event_queue.put('dialog_stop')
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def is_bot_stopped_listener(self):
        if not threads_event_queue.empty():
            queue_item = threads_event_queue.get_nowait()
            if queue_item == 'bot_stopped':
                self.bot_stopped_handler()
                return
            elif queue_item == 'error':
                self.error_handler()
                return
            else:
                threads_event_queue.put(queue_item)
        self.root.after(1000, self.is_bot_stopped_listener)

    def bot_stopped_handler(self):
        self.stop_bot()
        self.bot_state.config(text='Bot is now stopped.')

    def error_handler(self):
        self.stop_bot()
        self.bot_state.config(text='An error occured.\nBot is now stopped.')
        raise_app(root=self.root)

    @staticmethod
    def show_options(options, row, col):
        row = row
        for btn in options:
            btn.grid(row=row, column=col, sticky='w', padx=10)
            row += 1

    @staticmethod
    def start_bot_thread():
        t1 = Thread(target=bot_thread)
        t1.setDaemon(True)
        t1.start()


if __name__ == '__main__':
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()
