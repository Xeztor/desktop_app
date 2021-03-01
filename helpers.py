from tkinter import Checkbutton, StringVar, Label
import json
import os
import subprocess
import platform


class VGACheckButton(Checkbutton):
    def __init__(self, root, vga_model):
        self.selected = StringVar()
        self.model = vga_model
        super().__init__(
            root,
            compound="right",
            text=vga_model,
            offvalue='',
            onvalue='selected',
            variable=self.selected,
            font="arial 10",
        )


class BasicLabel(Label):
    def __init__(self, root, text, font_size):
        super().__init__(
            root,
            text=text,
            font=f'arial {font_size}',
        )


class AskedList:
    def __init__(self, root, start_row):
        self.root = root
        self.start_row = start_row

        self.asked_dict = {}
        self.update_asked_list()

        self.models_labels_list = []
        self.update_labels_list()

    def update_asked_list(self):
        self.asked_dict = get_asked_models()

    def update_labels_list(self):
        self.models_labels_list.clear()
        self.update_asked_list()
        for chipset, models in self.asked_dict.items():
            for model_name in models:
                self.models_labels_list.append(BasicLabel(self.root, model_name, 10))

    def show(self):
        crnt_row = self.start_row
        for i in range(len(self.models_labels_list)):
            self.models_labels_list[i].grid(row=crnt_row + i, column=0, padx=10, sticky='w')
            crnt_row += 1

    def destroy(self):
        for label in self.models_labels_list:
            label.destroy()

    def update(self):
        self.destroy()
        self.update_labels_list()
        self.show()


class AvailableList:
    def __init__(self, root):
        self.root = root
        self.models_labels_list = []

    def update_labels_list(self, new_models):
        self.models_labels_list.clear()
        available_models_list = new_models
        for model in available_models_list:
            self.models_labels_list.append(BasicLabel(self.root, model, 10))

    def show(self, start_row):
        for i in range(len(self.models_labels_list)):
            self.models_labels_list[i].grid(row=start_row + i, column=0, padx=10, sticky='w')

    def destroy(self):
        for label in self.models_labels_list:
            label.destroy()

    def update(self, new_models):
        if self.models_labels_list:
            self.destroy()
        self.update_labels_list(new_models)


def get_selected(options):
    selected = []
    for btn in options:
        if btn.selected.get():
            selected.append(btn.model)

    return selected


def get_all_models(chipset):
    chipset = chipset.lower()
    with open(f'./models/{chipset}.txt', 'r') as file:
        models = json.load(file)

    models = models['models']

    return models


def get_asked_models():
    with open(f'./asked.txt', 'r') as file:
        asked_models = json.load(file)

    return asked_models


def get_vga_options(root, chipset):
    models = get_all_models(chipset)
    options = [VGACheckButton(root, model) for model in models]

    return options


def raise_app(root):
    root.attributes("-topmost", True)
    if platform.system() == 'Darwin':
        tmpl = 'tell application "System Events" to set frontmost of every process whose unix id is {} to true'
        script = tmpl.format(os.getpid())
        output = subprocess.check_call(['/usr/bin/osascript', '-e', script])
    root.after(0, lambda: root.attributes("-topmost", False))
