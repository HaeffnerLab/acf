import numpy as np
import PyQt5
from PyQt5.QtWidgets import QMainWindow, QTreeView, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import PyQt5.Qt as Qt
from artiq.applets.simple import SimpleApplet

#from acf.parameter_manager import ParameterManager


class ParameterWidget(QMainWindow):

    def __init__(self, args, req):
        super().__init__()
        self.setup()

        self.req = req
        """print(dir(self.req.ipc.write_pyon(
                        {"action": "get_dataset",
                         "key": "a",
                         "value": 5,
                         "metadata": {},
                         "persist": None})))"""

        # Set this to true before updating item text from dataset to avoid triggering
        # dataset update from item changed event
        self.updating_item_from_datasets = False

        # Same but the opposite direction
        self.updating_datasets_from_item = False

    def setup(self):

        # Create the Tree View as the main display for the widget
        self.view = QTreeView()
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setCentralWidget(self.view)

        # Create the item model and import data from the parameter manager
        self.model = QStandardItemModel(0, 2)
        self.model.itemChanged.connect(self.param_changed)
        self.model.setHorizontalHeaderLabels(["Parameter", "Value"])
        """for i in range(5):
            #item = QStandardItem()
            #item.insertRow(0, [QStandardItem("hi"), QStandardItem("there")])
            #item.setText([f"hi {i}", "lol"])
            #item.setData(["hi", "there"])
            itemitem = QStandardItem(f"value {i}")
            itemitem.setData(f"item parameter value {i}")
            items = [QStandardItem("name"), itemitem]
            self.model.appendRow(items)
        for i in range(5):
            nameitem = QStandardItem("name")
            nameitem.setEditable(False)
            subnameitem = QStandardItem("subname")
            subnameitem.setEditable(False)
            nameitem.appendRow([subnameitem, QStandardItem(f"subvalue {2*i}")])
            self.model.appendRow(nameitem)"""
        #parent_item.appendRow(item)

        #self.model = QStandardItemModel()
        #parentItem = self.model.invisibleRootItem()
        #for i in range(0, 4):
            #item = QStandardItem("hi hi")
            #parentItem.appendRow(item)
            #parentItem = item

        self.view.setModel(self.model)
        #self.view.expandAll()
        #for column in range(self.model.columnCount()):
            #self.view.resizeColumnToContents(column)

        #self.update_actions()

    def param_changed(self, item):

        # Don't update artiq dataset if the item was updated to reflect a change in the
        # artiq dataset
        if self.updating_item_from_datasets:
            self.updating_item_from_datasets = False
            return

        print("ITEM CHANGED")
        print(item)
        print(item.text())

        name_item = self.model.item(item.row(), item.column() - 1)
        dataset_name = f"__param__{name_item.text()}"
        value = item.text()
        if value.replace(".", "").isnumeric():
            value = float(value)
        self.updating_datasets_from_item = True
        self.req.set_dataset(dataset_name, value)

    #def retranslateUi(self):
        #pass
        #self.setColumnCount(2)
        #self.setHeaderLabels(["Parameter", "Value"])
        #self.addTopLevelItems([QTreeWidgetItem(["hi", "5"])])

    def data_changed(self, value, metadata, persist, mod_buffer):

        # Don't update value if the dataset update was from a manual parameter update
        # This techinically causes a race condition if the flag is set and then another
        # dataset is changed before the dataset changed for this parameter is handled here,
        # but this is unlikely enough that this should be fine.
        if self.updating_datasets_from_item:
            self.updating_datasets_from_item = False
            return

        print("value, metadata, persist, mod_buffer")
        print(value)
        print(metadata)
        print(persist)
        print(mod_buffer)

        mod = mod_buffer[0]

        if mod["action"] == "init":
            # Initialize the table
            for dataset_name, dataset_value in value.items():
                # TODO Replace __param__ with dataset_prefix from ParameterManger
                # See lower TODO
                param_name = dataset_name.removeprefix("__param__")
                self.add_param_to_model(param_name, dataset_value)

        elif mod["action"] == "setitem":
            param_name = mod["key"].removeprefix("__param__")
            param_value = mod["value"][1]

            # Get the item corresponding to the name of the parameter
            model_name_items = self.model.findItems(param_name, flags=Qt.Qt.MatchExactly, column=0)

            if len(model_name_items) == 0:

                # Create a new row for the new item
                self.add_param_to_model(param_name, param_value)

            elif len(model_name_items) == 1:

                # Update the existing item
                model_name_item = model_name_items[0]
                row = model_name_item.row()
                column = model_name_item.column()
                model_value_item = self.model.item(row, column + 1)
                self.updating_item_from_datasets = True
                model_value_item.setText(str(param_value))

            else:
                raise RuntimeError(f"Found {len(model_name_items)} items in model with name {param_name}, should be 0 or 1.")
        elif mod["action"] == "delitem":
            param_name = mod["key"].removeprefix("__param__")
            model_name_items = self.model.findItems(param_name, flags=Qt.Qt.MatchExactly, column=0)
            if len(model_name_items) == 1:
                self.model.takeRow(model_name_items[0].row())
            if len(model_name_items) > 1:
                raise RuntimeError("More than 1 row matches item to be deleted.")


    def add_param_to_model(self, name, value):
        """Add a parameter to the model to be displayed.

        Args:
            name (str): The name of the parameter Should not include the parameter manager prefix.
            value (?): The value of the parameter.
        """
        name_item = QStandardItem(name)
        name_item.setEditable(False)
        value_item = QStandardItem(str(value))
        self.model.appendRow([name_item, value_item])



"""class MyApplet(SimpleApplet):
    
    def __init__(self):
        super().__init__(ParameterWidget)

        self.main_widget.self.model.itemChanged.connect(self.do_thing)

    def do_thing(self):
        print("I'm the apple!")"""

class GetParametersApplet(SimpleApplet):
    """A simple applet that adds __param__ to dataset prefixes so that it gets
    updates to all the datasets being used as system parameters. Note that this
    prefix __param__ comes from """

    def args_init(self):
        super().args_init()
        self.dataset_prefixes.append("__param__")

        # TODO: Figure out how to import ACF so the above line can be replaced with this
        # so that dataset_prefix is only defined in 1 location
        #self.dataset_prefixes.append(ParameterManager.dataset_prefix)

def main():
    #widget = QtWidgets.QTreeWidget()
    #applet = SimpleApplet(QtWidgets.QTreeWidget)
    applet = GetParametersApplet(ParameterWidget)
    #applet = MyApplet()
    applet.run()


if __name__ == "__main__":
    main()
