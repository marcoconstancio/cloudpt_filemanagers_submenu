Description
===========

Cloudpt extensions for linux file managers.

Current tested file managers:

* Caja 1.4 - http://mate-desktop.org/applications/
* Nautilus 3.4.2 - https://live.gnome.org/Nautilus
* Thunar 1.4 - http://docs.xfce.org/xfce/thunar/start


Screenshots
===========

![Screenshot1](https://raw.github.com/marcoconstancio/cloudpt_filemanagers_submenu/master/screen1.jpg)
![Screenshot2](https://raw.github.com/marcoconstancio/cloudpt_filemanagers_submenu/master/screen2.jpg)


Instalation
==================

On your browser:	

* Login to your cloudpt account
* Go to **API->As Minhas Aplicações->Create a cloudpt app** and create application access, choose a name, select the **Out of band** option and leave **Sandbox** unchecked and save. 
* Click on *Edit app edits* and copy the **Consumer key** and **Segredo** keys.


Caja
====

Install the following packages:

* caja 
* python-caja
* python-gtk

On caja:

* Copy *cloudpt_caja_submenu.py* and *cloudpt.png* to *~/.local/share/caja-python/extensions* or */usr/share/share/caja-python/extensions* (it might be necessary to create the directories)
* Restart caja
* Right-click while inside your home folder a select *CloudPT->Config CloudPT*
* Insert the **Consumer key** and **Consumer secret** obtained earlier and press the *Link account button*
* Click the **HERE** link, authorize the application a copy the pin from the browser to the dialog box and press the ok button.
* Select the cloutpt dir and press the ok.
* Restart caja.


Nautilus
======================

Install the following packages:

* nautilus 
* python-nautilus
* python-gtk

On nautilus:

* Copy *cloudpt_nautilus_submenu.py* and *cloudpt.png* to *~/.local/share/nautilus-python/extensions* or */usr/share/share/nautilus-python/extensions* (it might be necessary to create the directory)
* Restart caja
* Right-click while inside your home folder a select *CloudPT->Config CloudPT*
* Insert the **Consumer key** and **Consumer secret** obtained earlier and press the *Link account button*
* Click the **HERE** link, authorize the application a copy the pin from the browser to the dialog box and press the ok button.
* Select the cloutpt dir and press ok.
* Restart nautilus.


Thunar
======================

Install the following packages:

* thunar 
* python-nautilus
* thunarx-python

On thunar:

* Determine the directory where the thunarx-python extensions are placed by running **THUNARX_PYTHON_DEBUG=all thunar** on a console and checking the directory **thunarx\_python\_load\_dir**. Some common directories (you may need to create them) are:
	* ~/.local/share/thunarx-python
	* /usr/share/thunarx-python/extensions
	* on 32bits: /usr/lib/thunarx-1/python or /usr/lib/thunarx-2/python
	* on 64bits: /usr/lib/x86\_64-linux-gnu/thunarx-1/python or /usr/lib/x86\_64-linux-gnu/thunarx-2/python
* Copy *cloudpt_thunar_submenu.py* and *cloudpt.png* to extension directory
* Restart thunar
* Right-click while inside your home folder a select *CloudPT->Config CloudPT*
* Insert the **Consumer key** and **Consumer secret** obtained earlier and press the *Link account button*
* Click the **HERE** link, authorize the application a copy the pin from the browser to the dialog box and press the ok button.
* Select the cloutpt dir and press ok.
* Restart nautilus.


Notes
=====

* Once the CloudPT folder is selected in *CloudPT->Config CloudPT* area, the submenu will only be displayed in that folder.
* All the configuration (and keys) is saved in *~/.cloudpt/cloudpt.ini* on your home folder. Make sure the directory *~/.cloudpt* exists so that configuration is correctly saved. In order to reset the configuration, close the file manager, and use **rm -rif ~/.cloudpt/cloudpt.ini** on terminal.
* Make sure the cloudpt client is running so that the resquested actions, like recovering a file revision, are applied.