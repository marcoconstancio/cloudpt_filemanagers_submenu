Description
===========

Cloudpt extensions for linux file managers.

Current tested file managers:

* Caja 1.4 - http://mate-desktop.org/applications/
* Nautilus 3.4.2 - https://live.gnome.org/Nautilus

Screenshots
===========

![Screenshot1](https://github.com/marcoconstancio/cloudpt_filemanagers_submenu/blob/master/screen1.jpg)
![Screenshot2](https://github.com/marcoconstancio/cloudpt_filemanagers_submenu/blob/master/screen2.jpg)

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
* gir1.2-caja
* python-gtk

On caja:

* Copy *cloudpt_caja_submenu.py* and *cloudpt.png* to *.local/share/caja-python/extensions* (it might be necessary to create the directories)
* Restart caja
* Right-click while inside you home folder a select *CloudPT->Config CloudPT*
* Insert the **Consumer key** and **Consumer secret** obtained earlier and press the *Link account button*
* Click the **HERE** link, authorize the application a copy the pin from the browser to the dialog box and press the ok button.
* Select the cloutpt dir and press the ok.
* Restart caja.

Nautilus
======================

Install the following packages:

* nautilus 
* python-nautilus
* gir1.2-nautilus
* python-gtk

On nautilus:

* Copy *cloudpt_nautilus_submenu.py* and *cloudpt.png* to *.local/share/nautilus-python/extensions* (it might be necessary to create the directory)
* Restart caja
* Right-click while inside you home folder a select *CloudPT->Config CloudPT*
* Insert the *Consumer key* and *Consumer secret* obtained earlier and press the *Link account button*
* Click the **HERE** link, authorize the application a copy the pin from the browser to the dialog box and press the ok button.
* Select the cloutpt dir and press ok.
* Restart nautilus.


Notes
=====

* Once the CloudPT folder is selected in *CloudPT->Config CloudPT* area the submenu will only be displayed in that folder.
* All the configuration (and keys) is saved in *.cloudpt/cloudpt.ini* on your home folder. Make sure the directory *.cloudpt* exists so that configuration is saves correctly. In order to reset the configuration, close caja, and use **rm -rif ~./cloudpt/cloudpt.ini** on terminal.
* Make sure the cloudpt is running so that the resquested actions (like recovering a file revision) are applied.

License
=====

The files on this repo are free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. They are distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY. See the GNU General Public License for more details.