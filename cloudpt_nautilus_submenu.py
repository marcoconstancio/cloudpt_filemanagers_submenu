# coding: utf-8

from gi.repository import Nautilus, GObject, Gtk, GdkPixbuf
import time, random
import urlparse, httplib
import oauth2 as oauth
import urllib, cgi
import json, ConfigParser
import re
import os, sys
from os.path import expanduser, realpath, basename

class CloudPtExtension(GObject.GObject, Nautilus.MenuProvider):
    home_dir = expanduser("~")
    config_data = { 'request_token_url':'https://cloudpt.pt/oauth/request_token',
                    'access_token_url':'https://cloudpt.pt/oauth/access_token',
                    'authorize_url':'https://cloudpt.pt/oauth/authorize',
                    'api_url':'https://api.cloudpt.pt/Storage/CloudPT',
                    'consumer_key':'',
                    'consumer_secret':'',
                    'oauth_token':'',
                    'oauth_token_secret':'',
                    'cloudpt_dir':home_dir, #'cloudpt_dir':os.path.join(home_dir,'CloudPT'),
                    'config_file_path':os.path.join(home_dir,'.cloudpt','cloudpt.ini'),
                    'cloudpt_dir_len':os.path.join(home_dir,'CloudPT').__len__() }
    
    # Caja crashes if a plugin doesn't implement the __init__ method.
    # See Bug #374958
    def __init__(self):
        self.extension_dir = os.path.dirname( __file__ )
        pass

    # Function is called when user selects files. 
    def get_file_items(self, window, files):
        if os.path.exists(self.config_data['config_file_path']) == False:
            self.save_config_file();

        self.read_config_file()

        if files:
            file = files[0]
            # Only local files, no urls or remote addresses
            if file.get_uri_scheme() != 'file':
                return

            selection = urllib.unquote(file.get_uri()[7:])
            parent_dir = selection[:self.config_data['cloudpt_dir_len']] 

            # Shows menu only when inside the cloudpt folder
            if self.config_data['cloudpt_dir'] == parent_dir:
                # builds menus -> name, label, icon, function, function parameter
                if self.config_data['oauth_token'] and self.config_data['oauth_token_secret']:   
                    menu_layout = [["recover_previous_version","Recover previous version",Gtk.STOCK_DND_MULTIPLE,self.recover_file_revision,selection],
                                    ["create_link","Create link",Gtk.STOCK_CONNECT,self.get_file_link,selection],
                                    ["delete_link","Delete link",Gtk.STOCK_DISCONNECT,self.delete_link,selection],
                                    ["share_folder","Share folder",Gtk.STOCK_DIRECTORY,self.share_folder,selection],
                                    ["config_cloud_pt","Config CloudPT",Gtk.STOCK_PROPERTIES,self.config_cloud_pt,None]]
                else:
                     menu_layout = [["config_cloud_pt","Config CloudPT",Gtk.STOCK_PROPERTIES,self.config_cloud_pt,None]]                   

                

                top_menuitem = Nautilus.MenuItem(name='CajaPython::cloudpt_folder',label='CloudPT',tip='',icon=os.path.join(self.extension_dir,'cloudpt.png'))
   
                submenu = Nautilus.Menu()
                top_menuitem.set_submenu(submenu)

                for menu_item_info in menu_layout:
                    sub_menuitem = Nautilus.MenuItem(name='CajaPython::'+menu_item_info[1], label=menu_item_info[1], tip='', icon=menu_item_info[2])
                    
                    if menu_item_info[4]:
                        sub_menuitem.connect("activate",menu_item_info[3],menu_item_info[4])
                    else:
                        sub_menuitem.connect("activate",menu_item_info[3])

                    submenu.append_item(sub_menuitem)

                return top_menuitem,
        return 

    # Funtion is called when the user right-click on a folder without selecting files.   
    def get_background_items(self, window, file):
        # Only local files, no urls or remote addresses
        if file.get_uri_scheme() != 'file':
            return
              
        current_dir = urllib.unquote(file.get_uri()[7:])
        folder_relative_path = current_dir[self.config_data['cloudpt_dir_len']:] 
        if folder_relative_path == "":
            folder_relative_path = "/"        

        # Shows menu only when inside the cloudpt folders
        if self.config_data['cloudpt_dir'] == current_dir[:self.config_data['cloudpt_dir_len']]:
            # builds menus -> name, label, icon, function, function parameter
            if self.config_data['oauth_token'] and self.config_data['oauth_token_secret']:  
                menu_layout = [["undelete_file_folder","Undelete file folder",Gtk.STOCK_UNDELETE,self.recover_files_folders,folder_relative_path],
                                ["config_cloud_pt","Config CloudPT",Gtk.STOCK_PROPERTIES,self.config_cloud_pt, None]]
            else:
                menu_layout = [["config_cloud_pt","Config CloudPT",Gtk.STOCK_PROPERTIES,self.config_cloud_pt, None]]


            submenu = Nautilus.Menu()
            for menu_item_info in menu_layout:
                sub_menuitem = Nautilus.MenuItem(name='CajaPython::'+menu_item_info[1],label=menu_item_info[1],tip='',icon=menu_item_info[2])

                if menu_item_info[4]:
                    sub_menuitem.connect("activate",menu_item_info[3],menu_item_info[4])
                else:
                    sub_menuitem.connect("activate",menu_item_info[3])

                submenu.append_item(sub_menuitem)

            menuitem = Nautilus.MenuItem(name='CajaPython::cloudpt_files',label='CloudPT',tip='',icon=os.path.join(self.extension_dir,'cloudpt.png'))
            menuitem.set_submenu(submenu)
            return menuitem,
        return
    
    # Saves config_data variable to config file
    def save_config_file(self):
        options = ['consumer_key','consumer_secret','oauth_token','oauth_token_secret','cloudpt_dir']
        with open(self.config_data['config_file_path'], "w+") as fd:
            fd.write("[config]\n")
            for opt in options:
                fd.write(opt+" = "+self.config_data[opt]+"\n")

    # Read config file to config_data variable
    def read_config_file(self):
        config_file = ConfigParser.ConfigParser()
        config_file.read(self.config_data['config_file_path'])

        options = ['consumer_key','consumer_secret','oauth_token','oauth_token_secret','cloudpt_dir']

        for opt in options:
            try:
                self.config_data[opt] = config_file.get('config', opt)
            except ConfigParser.NoOptionError, err:
                self.config_data[opt] = None
        try:
            self.config_data['cloudpt_dir_len'] = self.config_data['cloudpt_dir'].__len__()
        except err:
            pass    

    # Dialog box function. Display a message dialog box, but when default_value is set, it generates an input dialog box
    def show_dialog(self, message,default_value=None):
        # if default_value != None:
        #     icon = Gtk.MESSAGE_QUESTION
        # else:
        #     icon = Gtk.MESSAGE_INFO

        dialog = Gtk.MessageDialog(None, Gtk.MessageType.OTHER,4,Gtk.ButtonsType.OK,None)    
        dialog.set_markup(message)
        text = None

        if default_value != None:
            entry = Gtk.Entry()
            entry.set_text(default_value)
            entry.connect("activate", self.dialog_key_pressed_response, dialog, Gtk.ResponseType.OK)
            
            hbox = Gtk.HBox()
            hbox.pack_end(entry, True, True, 0)
            dialog.vbox.pack_end(hbox, True, True, 0)
                
        dialog.show_all()
        dialog.run()
        
        if default_value != None:
            text = entry.get_text()
        
        dialog.destroy()

        if default_value != None:
            return text.strip()          
    
    # Necessary function for the dialog box to accept response when user presses the ENTER ley   
    def dialog_key_pressed_response(self, entry, dialog, response):
        dialog.response(response)

    # Save the sync folder path when a user selects another folder 
    def cloudpt_dir_select(self, widget):
        self.config_data['cloudpt_dir'] = widget.get_filename()
        self.save_config_file()

    # Config dialog box
    def config_cloud_pt(self,widget):      
        dialog = Gtk.MessageDialog(None, Gtk.MessageType.OTHER ,4,Gtk.ButtonsType.OK,None)
            
        dialog.set_markup("To get the keys, login to you account and go to:\n<b>API->As Minhas Aplicações->Create a cloudpt app</b>\nChoose a name, select the <b>Out of band</b> option and leave <b>Sandbox</b> unchecked.")
           
        keys_frame = Gtk.Frame()
        keys_frame.set_label("Keys")
        misc_frame = Gtk.Frame()
        misc_frame.set_label("Misc")

        consumer_key_entry = Gtk.Entry()
        consumer_key_entry.set_text(self.config_data['consumer_key'])
        consumer_key_entry.set_size_request(360,25)

        consumer_secret_entry = Gtk.Entry()
        consumer_secret_entry.set_text(self.config_data['consumer_secret'])
        consumer_secret_entry.set_size_request(340,25)

        link_account_entry = Gtk.Button("Link account")
        link_account_entry.connect("clicked", self.link_account, consumer_key_entry, consumer_secret_entry)

        hbox1 = Gtk.HBox(False, 1)
        hbox1.pack_start(Gtk.Label('Consumer key:'), True, True, 0)
        hbox1.pack_end(consumer_key_entry, True, True, 0)

        hbox2 = Gtk.HBox(False, 1)   
        hbox2.pack_start(Gtk.Label('Consumer secret:'), True, True, 0)
        hbox2.pack_end(consumer_secret_entry, True, True, 0)   

        vbox1 = Gtk.VBox(False, 5)
        vbox1.pack_start(hbox1, True, True, 0)
        vbox1.pack_start(hbox2, True, True, 0)
        vbox1.pack_start(link_account_entry, True, True, 0)
        keys_frame.add(vbox1)

        dir_select=Gtk.FileChooserButton('Current Directory')
        dir_select.set_action(Gtk.FileChooserAction.SELECT_FOLDER) 
        dir_select.set_filename(self.config_data['cloudpt_dir'])
        dir_select.connect("selection-changed",self.cloudpt_dir_select)

        hbox3 = Gtk.HBox(False, 1)
        hbox3.pack_start(Gtk.Label('CloudPT folder:'), True, True, 0)
        hbox3.pack_end(dir_select, True, True, 0)   

        misc_frame.add(hbox3)

        dialog.vbox.pack_start(keys_frame, True, True, 0)
        dialog.vbox.pack_start(misc_frame, True, True, 0)
        
        dialog.show_all()
        dialog.run()
        self.config_data['consumer_key'] = consumer_key_entry.get_text()
        self.config_data['consumer_secret'] = consumer_secret_entry.get_text()
        self.save_config_file()
        dialog.destroy()

    # links the account 
    def link_account(self, widget,consumer_key,consumer_secret):
        consumer_key = consumer_key.get_text()
        consumer_secret = consumer_secret.get_text()
        
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer)

        resp, content = client.request(self.config_data['request_token_url'], "POST", urllib.urlencode({'oauth_callback':'oob'}))
        if resp['status'] == '200':
            request_token = dict(urlparse.parse_qsl(content))
            oauth_verifier = self.show_dialog("Click <a href='%s?oauth_token=%s'>HERE</a>, authorize the application and copy the pin:" % (self.config_data['authorize_url'], request_token['oauth_token']),"")
         
            token = oauth.Token(request_token['oauth_token'],request_token['oauth_token_secret'])
            token.set_verifier(oauth_verifier)
            client = oauth.Client(consumer, token)

            resp, content = client.request(self.config_data['access_token_url'], "POST")
            if resp['status'] == '200':
                access_token = dict(urlparse.parse_qsl(content))

                self.config_data['oauth_token'] = access_token['oauth_token']
                self.config_data['oauth_token_secret'] = access_token['oauth_token_secret']
                self.save_config_file()

                self.show_dialog("The application was successfully authorized.",None)
            else:
                self.show_dialog("There was an error in authorizing the application. Please verify that you granted access to the application and inputed the pin correctly.",None)
        else:
            self.show_dialog("Invalid response from server. Please verify the consumer key and secret.",None)    

    # Recover deleted folder and files 
    def recover_files_folders(self,widget,current_dir):
        files_folder_list = []
        selected_file_folder_list = []
        
        files_folder_list_data = self.get_deleted_files_folders(current_dir)
        if files_folder_list_data:
            for file_folder in files_folder_list_data:
                files_folder_list.append([file_folder['path'][1:],file_folder['is_dir']])
            
            selected_file_folder_list = self.select_file_folder_dialog(files_folder_list,'Please select the file(s) and folder(s) to restore.',True)
            
            num_sucesses = 0
            num_failures = 0
            consumer = oauth.Consumer(self.config_data['consumer_key'], self.config_data['consumer_secret'])
            access_token = oauth.Token(self.config_data['oauth_token'], self.config_data['oauth_token_secret'])
            client = oauth.Client(consumer, access_token)

            for files_folder in selected_file_folder_list:
                response = client.request(self.config_data['api_url'] + '/UndeleteTree/cloudpt/' + urllib.quote(files_folder), 'POST')
                # self.show_dialog(str(response),None)
                if response[0]['status'] == "404":
                    num_failures+=1
                elif response[0]['status'] == "200":
                    num_sucesses+=1

            self.show_dialog("<b>Result</b>: "+str(num_sucesses)+" sucesses and "+str(num_failures)+" failures.",None)            
        else:
            self.show_dialog("This folder has no deleted files or folders.",None)            
            
    # return array with a list of deleted files and folder 
    def get_deleted_files_folders(self,folder_list_path):
        consumer = oauth.Consumer(self.config_data['consumer_key'], self.config_data['consumer_secret'])
        access_token = oauth.Token(self.config_data['oauth_token'], self.config_data['oauth_token_secret'])
        client = oauth.Client(consumer, access_token)
        folder_list_url = self.config_data['api_url'] + '/List/cloudpt' + urllib.quote(folder_list_path)

        folder_list = []
        folder_list_deleted_files = []

        # Get existing files
        response = client.request(folder_list_url, 'GET')  
        if response[0]['status'] == "404":
            folder_list_deleted_files = None
        else:
            response_array = json.loads(response[1])

            for file_data in response_array['contents']:
                folder_list.append(file_data['path'])
            
            # Get existing files INCLUDING deleted ones and compares with the previous list
            response = client.request(folder_list_url + '?' + urllib.urlencode({'include_deleted':'true','order_by':'folder'}), 'GET')
            response_array = json.loads(response[1])

            for file_data in response_array['contents']:
                if file_data['path'] not in folder_list:
                    folder_list_deleted_files.append(file_data)

        return folder_list_deleted_files

    # Dialog box for use file(s) selection
    def select_file_folder_dialog(self,file_folder_list=None,message='',multiple_selection=False):
        if self.config_data != None and file_folder_list != None:
            dialog = Gtk.MessageDialog(None,Gtk.MessageType.OTHER,4,Gtk.ButtonsType.OK,None)
            dialog.set_markup(message)
            #dialog.set_size_request(450,-1)

            # Icon render
            folder_pixbuf = dialog.render_icon(Gtk.STOCK_DIRECTORY,size=Gtk.IconSize.BUTTON,detail=None) 
            file_pixbuf = dialog.render_icon(Gtk.STOCK_FILE,size=Gtk.IconSize.BUTTON,detail=None) 
            
            #Tree view, add the filenamess to the treestore (model)
            dir_treeview = Gtk.TreeView()
            dir_treestore = Gtk.TreeStore(bool, GdkPixbuf.Pixbuf,str)
            for file_folder in file_folder_list:
                if file_folder[1]:
                    dir_treestore.append(None, (False, folder_pixbuf, file_folder[0]))
                else:
                    dir_treestore.append(None, (False, file_pixbuf, file_folder[0]))

            dir_treeview.set_model(dir_treestore)  

            # Creates the checkboxes
            render_toggle = Gtk.CellRendererToggle()
            render_toggle.set_property('activatable', True)
            render_toggle.connect('toggled',self.column1_toggled_combobox,dir_treestore,multiple_selection)

            dir_treeview_column1 = Gtk.TreeViewColumn("",render_toggle,active=0)

            # Create icon and filename text a append to second column
            dir_treeview_column2 = Gtk.TreeViewColumn()

            render_pixbuf = Gtk.CellRendererPixbuf()
            render_text = Gtk.CellRendererText()
            dir_treeview_column2.pack_start(render_pixbuf, expand=False)
            dir_treeview_column2.add_attribute(render_pixbuf, 'pixbuf', 1)
            dir_treeview_column2.pack_start(render_text, expand=False)
            dir_treeview_column2.add_attribute(render_text, 'text', 2) 
           
            # setup treeview
            dir_treeview.append_column(dir_treeview_column1)
            dir_treeview.append_column(dir_treeview_column2)

            # setup scrollable area
            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_border_width(1)
            scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
            scrolled_window.add_with_viewport(dir_treeview)
            scrolled_window.set_size_request(400,200)

            # setup the dialog
            dialog.vbox.pack_start(scrolled_window, True, True, 0)
            dialog.show_all()
            dialog.run()

            selected_file_folder_list = []
            for row in dir_treestore:
                if row[0]:
                    selected_file_folder_list.append(row[2])

            dialog.destroy()
            return selected_file_folder_list

    # Maintains the toggled combobox in the select_file_folder_dialog
    def column1_toggled_combobox(self, cell, path_str, model, multiple_selection):
        if multiple_selection == False:
            iter = model.get_iter_first()
            model.set(iter, 0, False)
            while not iter == None:
                model.set(iter, 0, False)
                iter = model.iter_next(iter) 
        
        # get toggled iter
        iter = model.get_iter_from_string(path_str)
        toggle_item = model.get_value(iter, column=0)
        # change value
        toggle_item = not toggle_item
        # update models
        model.set(iter, 0, toggle_item) 
        return            

    # Recover a file previous revision
    def recover_file_revision(self,widget,file):
        if os.path.isdir(file) == True:
            self.show_dialog("The first selection is a folder. It is only possible to retrieve file revisions.")
        else:
            consumer = oauth.Consumer(self.config_data['consumer_key'], self.config_data['consumer_secret'])
            access_token = oauth.Token(self.config_data['oauth_token'], self.config_data['oauth_token_secret'])
            client = oauth.Client(consumer, access_token)
            filename_relative_path = file[self.config_data['cloudpt_dir_len']:] 

            # Get all revisions and displays them in the select file folder dialog
            response = client.request(self.config_data['api_url']  + '/Revisions/cloudpt' + urllib.quote(filename_relative_path), 'GET')
            if response[0]['status'] == "404":
                self.show_dialog("Error on retrieving revisions for this file.")            
            elif response[0]['status'] == "200":
                response_array = json.loads(response[1])
                file_dates_list = [] 
                file_revisions_list = {} 
                
                for file_rev in response_array:

                    mapping = [('Mon','Seg'),('Tue','Ter'),('Wed','Qua'),('Thu','Qui'),('Fri','Sex'),('Sat','Sab'),('Sun','Dom'),
                               ('Feb','Fev'),('Abr','Apr'),('May','Mai'),('Aug','Ago'),('Sep','Set'),('Oct','Out'),('Dec','Dez')]

                    date_str = str(file_rev['modified'])           
                    for k, v in mapping:
                        date_str = date_str.replace(k, v)

                    item_entry = date_str[:date_str.find(' +')]+' - '+file_rev['size']
                    file_dates_list.append([item_entry,False])
                    file_revisions_list[item_entry] = file_rev['rev']

                selected_files_revision = self.select_file_folder_dialog(file_dates_list,'Please select a revision to restore.')
                
                if selected_files_revision:
                    response = client.request(self.config_data['api_url'] + '/Restore/cloudpt' + urllib.quote(filename_relative_path), 'POST',urllib.urlencode({'rev':file_revisions_list[selected_files_revision[0]]}))
                    if response[0]['status'] == "404":
                        self.show_dialog("Error on recovering the selected revision for the file.") 
                    elif response[0]['status'] == "200":
                        self.show_dialog("The recover of of the selected revision was successful.") 

    # Returns a hyperlink for a seletect file 
    def get_file_link(self, widget,file):
        consumer = oauth.Consumer(self.config_data['consumer_key'], self.config_data['consumer_secret'])
        access_token = oauth.Token(self.config_data['oauth_token'], self.config_data['oauth_token_secret'])
        client = oauth.Client(consumer, access_token)
        filename_relative_path = file[self.config_data['cloudpt_dir_len']:] 

        # request file link
        response = client.request( self.config_data['api_url'] + '/Shares/cloudpt'+ urllib.quote(filename_relative_path), 'POST')
        if response[0]['status'] == "404":
            self.show_dialog("Error on creating the link for the selected file.")            
        elif response[0]['status'] == "200":
            response_array = json.loads(response[1])     
            self.show_dialog("The link for "+filename_relative_path+" is:\n<a href='"+response_array['url']+"'>"+response_array['url']+"</a>")  

    # Delete a file hyperlink for a seletect file 
    def delete_link(self,widget,file):       
        consumer = oauth.Consumer(self.config_data['consumer_key'], self.config_data['consumer_secret'])
        access_token = oauth.Token(self.config_data['oauth_token'], self.config_data['oauth_token_secret'])
        client = oauth.Client(consumer, access_token)
        filename_relative_path = file[self.config_data['cloudpt_dir_len']:] 

        links_sharedids = {}

        response = client.request(self.config_data['api_url'] + '/ListLinks', 'GET')
        response_array = json.loads(response[1])
        for file_data in response_array:
            links_sharedids[file_data['path']] = file_data['shareid'] 

        try:   
            response = client.request(self.config_data['api_url'] + '/DeleteLink', 'POST', urllib.urlencode({'shareid': links_sharedids[filename_relative_path]}))
            if response[0]['status'] == "404":
                self.show_dialog("Error on deleting the link for the selected file.")            
            elif response[0]['status'] == "200":
                self.show_dialog("The link was deleted successfully")  
        except KeyError:
            self.show_dialog("There in no link associated with this file.")    

    # Allows folder sharing with other users, receives user emails 
    def share_folder(self,widget,file):
        if os.path.isdir(file) == True:
            inputed_email_strings = self.show_dialog("Insert a comma separated list of emails:","")  
            filename_relative_path = file[self.config_data['cloudpt_dir_len']:] 
            
            email_list = inputed_email_strings.split(",")
            email_array = []
            email_sucess_array = []

            for email_string in email_list:
                if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email_string.strip()) != None:
                    email_array.append(email_string.strip())

            if email_array:
                consumer = oauth.Consumer(self.config_data['consumer_key'], self.config_data['consumer_secret'])
                access_token = oauth.Token(self.config_data['oauth_token'], self.config_data['oauth_token_secret'])
                client = oauth.Client(consumer, access_token)

                for email_addr in email_array:
                    response = client.request(self.config_data['api_url'] + '/ShareFolder/cloudpt' +  urllib.quote(filename_relative_path), 'POST', urllib.urlencode({'to_email':email_addr}))
                    if response[0]['status'] == "200":
                        email_sucess_array.append(email_addr)

                if email_sucess_array:
                    self.show_dialog("The folder "+filename_relative_path+" was shared with the following emails:\n" + ", ".join(email_sucess_array))  
                else:
                    self.show_dialog("No invitions were sent. Check if this folder is synced with CloudPT." )  
            else:
                self.show_dialog("No valid email address were inputed." )  
        else:                  
            self.show_dialog("The selection is a file. Only folders can be shared.")
    
