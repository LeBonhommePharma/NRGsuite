'''
    NRGsuite: PyMOL molecular tools interface
    Copyright (C) 2011 Gaudreault, F., Morency, LP. & Najmanovich, R.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

from __future__ import print_function

'''
@title: Plugin_NRG suite (for Pymol)

@summary: Plugin that add NRG suite applications access via the pymol application

@organization: Najmanovich Research Group
@creation date:  Aug. 25, 2010
'''

import sys, os, stat
import platform

if sys.version_info[0] < 3:
    from Tkinter import *
    import tkMessageBox
else:
    from tkinter import *
    import tkinter.messagebox as tkMessageBox

import time

from pymol import cmd
pymol_major_version = int(cmd.get_version()[0][0])

'''=================================================================================================
FUNCTION get_default_path_for_OSid: returns the default (and preferred) installation path for any OS
================================================================================================='''
def get_default_path_for_OSid():
    # DETECT the operating system
    OS = platform.system().upper()
    OSid = 'UNKNOWN'

    # SET the configuration location
    if OS == 'LINUX' or OS == 'BSD':
        OSid = 'LINUX'
    elif OS == 'DARWIN':       
        OSid = 'MAC'    
    elif OS == 'WINDOWS' or OS == 'MICROSOFT' or OS == 'WIN32':
        OSid = 'WIN'
    else:
        OSid = 'UNKNOWN'

    if OSid == 'WIN':
        ProgramFiles = os.getenv('PROGRAMFILES')
        if ProgramFiles:
            Install_Dir = os.path.join(ProgramFiles,'NRGsuite')
        else:
            Install_Dir = os.path.join('C:\\','Program Files','NRGsuite')
            
    elif OSid == 'MAC':
        Install_Dir = os.path.join('/Applications','NRGsuite')

    else:
        Install_Dir = os.path.join('/usr','local','NRGsuite')

    return Install_Dir

# get the installation path of the NRGsuite with the ENV variable NRGSUITE_INSTALLATION or
# sets Install_Dir to the default (and preferred) installation directory
Install_Dir = os.environ.get('NRGSUITE_INSTALLATION', get_default_path_for_OSid())
 
if Install_Dir == '' or not os.path.isdir(Install_Dir):
    Install_Dir = get_default_path_for_OSid()

if os.path.isdir(Install_Dir) and sys.version_info > (2, 5):

    NRGsuite_Path = os.path.join(os.path.expanduser('~'),'Documents','NRGsuite')
    Plugin_Path = os.path.join(Install_Dir,'Plugin')
    Project_Path = os.path.join(Install_Dir,'Project')
    FlexAID_Path = os.path.join(Install_Dir,'FlexAID')
    GetCleft_Path = os.path.join(Install_Dir,'GetCleft')
    About_Path = os.path.join(Install_Dir,'About')
    
    if os.path.isdir(Project_Path) and os.path.isdir(FlexAID_Path) and \
       os.path.isdir(GetCleft_Path) and os.path.isdir(About_Path):

        # prime PyMOL's legacy plugin system
        try:
            from pymol.plugins import get_tk_root
            tk_root = get_tk_root()
        except ImportError:
            tk_root = None

        # Qt builds (PyMOL 2.5+ / 3) and `pymol -c` leave the legacy PMG
        # root as None. FlexAID and GetCleft construct Tk variables while
        # their modules are imported, which requires Tk's default root.
        if tk_root is None:
            tk_root = Tk()
            tk_root.withdraw()
    
        sys.path.append(Install_Dir)
        import Prefs
        
        sys.path.append(Plugin_Path)
        
        sys.path.append(Project_Path)
        import NewProject
        import LoadProject
        
        sys.path.append(FlexAID_Path)
        import FlexAID
        
        sys.path.append(GetCleft_Path)
        import GetCleft
        
        sys.path.append(About_Path)
        import About
        

        #------------------------------------------------------------------#
        #                        SETTING THE MENUS                         #
        #------------------------------------------------------------------# 
        
        def __init__(self):
            
            self.ProjectName = ''
            self.Project_Dir = ''
            
            self.RootPrefs = Prefs.Prefs()
            self.RootFlexAID = None         # FlexAID Toplevel()
            self.RootGetCleft = None        # GetCleft Toplevel()
            self.FlexAID = None             # FlexAId.displayFlexAID() object initialized when FlexAID menu item is clicked
            self.GetCleft = None            # GetCleft.displayGetCleft() object initialized when GetCleft menu item is clicked

            # ADD a new main menu named Project to the menu bar
            #self.menuBar.addmenu('NRGsuite', 'Najmanovich Research Group Suite')
            self.menuBar.addcascademenu('Plugin',
                        'NRGsuite',
                        'NRGsuite',
                        label = 'NRGsuite')

            #------------------------------------------------------------------
            # ADD a menu named Open New Project to the NRGsuite main menu
            self.menuBar.addmenuitem('NRGsuite', 'command',
                                     'CfgFile',
                                     label='   New Project...',
                                     command = lambda s=self, menuindex=0 : StartNewProject(s, menuindex))
            
            #------------------------------------------------------------------
            # ADD a menu named Open New Project to the NRGsuite main menu
            self.menuBar.addmenuitem('NRGsuite', 'command',
                                     'CfgFile',
                                     label='   Load Project...',
                                     command = lambda s=self, menuindex=1 : StartLoadProject(s, menuindex))
            
            #------------------------------------------------------------------
            # ADD a menu named Open New Project to the NRGsuite main menu
            self.menuBar.addmenuitem('NRGsuite', 'command',
                                     'CfgFile',
                                     label='   Close Project',
                                     command = lambda s=self, menuindex=2 : StartCloseProject(s, menuindex))
            
            # ADD a seperator to the main menu 
            self.menuBar.addmenuitem('NRGsuite','separator')
        
            #------------------------------------------------------------------
            # ADD a menu named Preferences
            self.menuBar.addmenuitem('NRGsuite', 'command',
                                     'CfgFile',
                                     label='   Preferences',
                                     command = lambda s=self, menuindex=4 : StartPreferences(s, menuindex))
            
            # ADD a seperator to the main menu 
            self.menuBar.addmenuitem('NRGsuite','separator')

            #------------------------------------------------------------------
            # ADD a menu named Open FlexAID to the NRGsuite main menu
            self.menuBar.addmenuitem('NRGsuite', 'command',
                                     'CfgFile',
                                     label='   Open FlexAID...',
                                     command = lambda s=self, menuindex=6 : StartFlexAID(s, menuindex))
            
            #------------------------------------------------------------------
            # ADD a menu named Open GetCleft to the NRGsuite main menu
            self.menuBar.addmenuitem('NRGsuite', 'command',
                                     'CfgFile',
                                     label='   Open GetCleft...',
                                     command = lambda s=self, menuindex=7 : StartGetCleft(s, menuindex))
            
            # ADD a seperator to the main menu 
            self.menuBar.addmenuitem('NRGsuite','separator')

            self.menuBar.addmenuitem('NRGsuite', 'command',
                                     'CfgFile',
                                     label='   About',
                                     command = lambda s=self, menuindex=9 : StartAbout(s, menuindex))

            # Make the Load  - Create projects button clickable only
            if pymol_major_version == 2:
                EnableDisableMenuQT(self, [True,True,False,True,False,False,True] )
            else:
                EnableDisableMenu(self, ['normal','normal','disabled','normal','disabled','disabled','normal'] )
        
        #================================================================================
        # STARTING GetCleft Conditional... 
        #================================================================================  
        def StartGetCleft(self, menuindex):
            
            self.RootGetCleft = Toplevel(self.root)
            self.GetCleft = GetCleft.displayGetCleft(self.RootGetCleft, self, menuindex, self.Project_Dir, Install_Dir,
                                     NRGsuite_Path, self.RootPrefs.OSid, self.root, 'NRGsuite - GetCleft', 500, 550, self.RootPrefs)
                
        #================================================================================
        # STARTING FlexAID Conditional... 
        #================================================================================  
        def StartFlexAID(self, menuindex):
            
            self.RootFlexAID = Toplevel(self.root)
            self.FlexAID = FlexAID.displayFlexAID(self.RootFlexAID, self, menuindex, self.Project_Dir, Install_Dir, 
                                   NRGsuite_Path, self.RootPrefs.OSid, self.root, 'NRGsuite - FlexAID', 800, 600, self.RootPrefs)
                
        #================================================================================
        # Load an existing Project
        #================================================================================
        def StartLoadProject(self, menuindex):
            
            LoadProject.displayLoadProject(Toplevel(self.root), self, menuindex, self.Project_Dir, Install_Dir,
                                           NRGsuite_Path, self.RootPrefs.OSid, self.root, 'NRGsuite - Load Project', 460, 350, self.RootPrefs)
            
        #================================================================================
        # Create a New Project
        #================================================================================
        def StartNewProject(self, menuindex):
                    
            NewProject.displayNewProject(Toplevel(self.root), self, menuindex, self.Project_Dir, Install_Dir,
                                         NRGsuite_Path, self.RootPrefs.OSid, self.root, 'NRGsuite - New Project', 420, 300, self.RootPrefs)
            
        #================================================================================
        # Loads the preferences menu to set the different options
        #================================================================================
        def StartPreferences(self, menuindex):
            Preferences = Prefs.displayPrefs(Toplevel(self.root), self, menuindex, self.Project_Dir, Install_Dir,
                               NRGsuite_Path, self.RootPrefs.OSid, self.root, 'NRGsuite - Preferences', 475, 260, self.RootPrefs)
            
        #================================================================================
        # Loads the about menu to see versionning
        #================================================================================
        def StartAbout(self, menuindex):
            
            About.displayAbout(Toplevel(self.root), self, menuindex, self.Project_Dir, Install_Dir,
                               NRGsuite_Path, self.RootPrefs.OSid, self.root, 'NRGsuite - About', 400, 350, self.RootPrefs)
        
        #================================================================================
        # Close the actual Project
        #================================================================================
        def StartCloseProject(self, menuitem):
                            
            if self.RootFlexAID is not None:
                if self.FlexAID is not None:
                    self.FlexAID.Quit()
                    self.FlexAID = None
                if self.RootFlexAID is not None:
                    # self.RootFlexAID.destroy()
                    self.RootFlexAID = None
                print('  FlexAID interface successfully closed.')
            
            if self.RootGetCleft is not None:
                if self.GetCleft is not None:
                    self.GetCleft.Quit()
                    self.GetCleft = None
                if self.RootGetCleft is not None:
                    # self.RootGetCleft.destroy()
                    self.RootGetCleft = None
                print('  GetCleft interface successfully closed.')
                   
            if pymol_major_version == 2:
                EnableDisableMenuQT(self, [True,True,False,True,False,False,True] )
            else:
                EnableDisableMenu(self, ['normal','normal','disabled','normal','disabled','disabled','normal'] )
            
            print('\n  The project \'' + self.ProjectName + '\' was closed.')

        #================================================================================        
        # Find children item in QMenu
        #================================================================================
        def findMenuItem(self, menu, name):
            for mi in menu.actions():
                if mi.text().strip() == name:
                    return mi
            return None

        #================================================================================        
        # Set the NRGsuite Menu Options to Enable when a Project is created or loaded.
        # Set to disable at start up or when a project is closed.
        #================================================================================
        def EnableDisableMenuQT(self, states):

            menuItems = [
                'New Project...', 'Load Project...', 'Close Project',
                'Preferences',
                'Open FlexAID...', 'Open GetCleft...',
                'About'
            ]

            NRGsuite = self.menuBar._menudict['NRGsuite']
            for menuItem in menuItems:
                mi = findMenuItem(self, NRGsuite, menuItem)
                if mi is None: continue
                mi.setEnabled(states.pop(0))
            
        #================================================================================        
        # Set the NRGsuite Menu Options to Enable when a Project is created or loaded.
        # Set to disable at start up or when a project is closed.
        #================================================================================
        def EnableDisableMenu(self, states):

            self.menuBar.component('NRGsuite-menu').entryconfig(0, state=states.pop(0))    # new
            self.menuBar.component('NRGsuite-menu').entryconfig(1, state=states.pop(0))    # load
            self.menuBar.component('NRGsuite-menu').entryconfig(2, state=states.pop(0))    # close
            self.menuBar.component('NRGsuite-menu').entryconfig(4, state=states.pop(0))    # preferences
            self.menuBar.component('NRGsuite-menu').entryconfig(6, state=states.pop(0))    # flexaid
            self.menuBar.component('NRGsuite-menu').entryconfig(7, state=states.pop(0))    # getcleft
            self.menuBar.component('NRGsuite-menu').entryconfig(9, state=states.pop(0))    # about
            
    else:
        tkMessageBox.showerror('Programs MISSING',
                               'The FlexAID and GetCleft applications ' + 
                               'need to be installed at this location: ' +
                               Install_Dir + '\n\nInstallation CANCELLED...')

elif sys.version_info < (2, 5):
    tkMessageBox.showerror('Unsupported Python version', 'The NRGsuite requires Python version 2.5 or newer. Your actual Python version is ' + sys.version + '. \n\nInstallation CANCELLED...')

else:
    tkMessageBox.showerror('NRGsuite not found',
                           'The NRGsuite applications need to be installed at this location: ' + 
                           Install_Dir + '\n\nInstallation CANCELLED...')
