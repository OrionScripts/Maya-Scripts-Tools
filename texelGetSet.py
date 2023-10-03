import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import maya.cmds as cmds
import math

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2 import __version__
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide import __version__

def maya_main_window():
    '''
    Return the Maya main window widget as a Python object.
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QWidget)

class MyWindow(QDialog):
    '''
    A custom QDialog class for the Texel Density Tool in Maya.
    '''
    def __init__(self, parent=None):
        '''
        Initializes the Texel Density Tool dialog window.

        Args:
            parent (QWidget): The parent widget for this dialog.
        '''
        super(MyWindow, self).__init__(parent)

        # Create buttons.
        self.button1 = QPushButton("Get Texel Density")
        self.button2 = QPushButton("Set Texel Density")

        # Create text field for current texel density.
        self.currentTexelDensity_textField = QLineEdit()

        # Create label for current texel density text field.
        self.label1 = QLabel("Current Texel Density")
      
        # Create text field for setting the texel density to a value.
        self.setTexelDensity_textField = QLineEdit()
        
        # Create a horizontal layout for the Set Texel Density button and the value.
        setTexelDensity_layout = QHBoxLayout()
        setTexelDensity_layout.addWidget(self.button2)
        setTexelDensity_layout.addWidget(self.setTexelDensity_textField)

        # Create a horizontal layout for the Current Texel Density button and the value.
        label_layout1 = QHBoxLayout()
        label_layout1.addWidget(self.label1)
        label_layout1.addWidget(self.currentTexelDensity_textField)

        # Create main layout and add widgets.
        layout = QVBoxLayout()
        layout.addWidget(self.button1)
        layout.addLayout(setTexelDensity_layout)
        layout.addLayout(label_layout1)
        self.setLayout(layout)

        # Set the window title and size.
        self.setWindowTitle("Ryan Amos - Texel Density Tool")
        self.resize(230, self.height())
        
        # Initialize targetTexelDensity variable.
        self.targetTexelDensity = None
        
        # Connect buttons and text fields to their respective methods.
        self.setTexelDensity_textField.editingFinished.connect(self.saveTexelDensity)
        self.button1.clicked.connect(self.getTexelDensity)
        self.button2.clicked.connect(self.set_texel_density)

    def saveTexelDensity(self):
        '''
        Save value from setTexelDensity_textField as an integer variable named targetTexelDensity.
        '''
        self.targetTexelDensity = int(self.setTexelDensity_textField.text())
        print(f"Target texel size set to: {self.targetTexelDensity}")
    
    def set_texel_density(self):
        '''
        Set Texel Density for selection, given a default texture resolution of 2048.
        '''
        sel = cmds.ls(sl=True, flatten=True)
        for i in sel:
            print("Selection: ",i)
        defaultTextureRes = 2048
        texDensity = self.targetTexelDensity
        scaleTarget = texDensity / defaultTextureRes
        
        for obj in sel:
            cmds.unfold(obj,i=5000,ss=0.001,gb=0,gmb=1,pub=0,ps=0,oa=0,us=1,s=scaleTarget)
            
        self.currentTexelDensity_textField.setText(str(self.targetTexelDensity))
    
    def getDistance2D(uvs):
        '''
        Return distance between two points in UV space.

        Args:
            uvs (list): A list of UV coordinates for two points.

        Returns:
            float: The distance between the two points in UV space.
        '''
        a = cmds.polyEditUV(uvs[0], q = True, u = True)
        b = cmds.polyEditUV(uvs[1], q = True, u = True)
        return (math.sqrt(math.pow(a[0] - b[0], 2) + math.pow(a[1] - b[1], 2)))

    def getDistance3D(verts):
        '''
        Return distance between two points in XYZ space.

        Args:
            verts (list): A list of XYZ coordinates for two points.

        Returns:
            float: The distance between the two points in XYZ space.
        '''
        a = cmds.pointPosition(verts[0])
        b = cmds.pointPosition(verts[1])
        
        return (math.sqrt(math.pow(a[0] - b[0], 2) + math.pow(a[1] - b[1], 2) + math.pow(a[2] - b[2], 2)))
    
    def getTexelDensity(self):
        '''
        Get average texel density for internal edges.
        '''
        defaultTextureRes = 2048
        # Get selected object.
        selectedObject = cmds.ls(sl = True)[0]    
        # Get edge lengths.
        numEdges = cmds.polyEvaluate(selectedObject, edge = True)
        # Skip shell edges; hard to get determine correct UVs to measure.
        numInternalEdges = 0
        # Average all edges to get overall texel density.
        texelDensity = 0 
        for i in range (numEdges):
            edge = selectedObject + '.e[' + str(i)+ ']'
            verts = cmds.polyListComponentConversion(edge, fromEdge = True, toVertex = True)
            verts = cmds.ls(verts, flatten = True)
            # Get edge len.
            edgeLen = getDistance3D(verts)  
            edgeLenToUnitRatio = 1 / edgeLen
            
            uvs = cmds.polyListComponentConversion(edge, fromEdge = True, toUV = True)
            uvs = cmds.ls(uvs, flatten = True)
            # Ignore shell edges - only process edges with 2 UVs.
            if len(uvs) == 2:
                # Increment internal edges counter.
                numInternalEdges += 1
                # Get UV edge len.
                uvEdgeLen = getDistance2D(uvs)
                # Get UV edge texel density.
                uvEdgeTexelDensity = defaultTextureRes * uvEdgeLen
                # Get edge texel density.
                edgeTexelDensity = uvEdgeTexelDensity * edgeLenToUnitRatio
                # Add each edge texel density.
                texelDensity += edgeTexelDensity
        # Get average texel density.
        texelDensity = texelDensity/numInternalEdges
        texelDensity = round(texelDensity)
        self.currentTexelDensity_textField.setText(str(texelDensity))
        self.setTexelDensity_textField.setText(str(""))
        print(f"Texel Density is {texelDensity}.")

# Math for get and set might be a tad wonky, but it gets the idea across well enough for what I have time for making.

def show_dialog():
    '''
    Show the dialog window.
    '''
    global dialog
    try:
        dialog.close()
    except:
        pass
    dialog = MyWindow(parent=maya_main_window())
    dialog.show()

if __name__ == "__main__":
    show_dialog()
