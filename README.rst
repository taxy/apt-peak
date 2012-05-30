packet-peak
===========

Egy segédprogram ami most került abba az állapotba, hogy közzé tegyem. Nagyon hasonlít a deborphan-hoz, de mivel annak funkcionalitása nem felelt meg 100%-osan arra amire használni szerettem volna, valamint annak a legfrissebb változata a deborphan 2.0 nem volt számomra lefordítható állapotban, inkább újraimplementáltam az egészet python-apt alapokon, mivel maga a program alaplogikája nem túl bonyolult. Így született a Packet Peak
A deborphan csak egyszerűen kilistázza azokat a csomagokat amiktől egyetlen másik csomag sem függ. Az én analógiám szerint ez azt jelenti, hogy ezek a csomagok a függőségi rendszer csúcsán vannak. A deborphan esetében azonban ez nem teljesen igaz, mert néha az ajánlott függőségek kört alkotnak a kötelező függőségekkel együtt. Ez az amit az én programom még külön figyel, és ha ilyen kört talál, akkor a kötelező függőségek csúcsát(mert azok nem alkothatnak kört természetesen) teszi be a listába. Így egy jó kivonatot kaphatunk a rendszerünkben található csomagokról. Általában ezt arra lehet használni, hogy kiszelektáljuk a szemetet, de készíthetünk a segítségével "tipikus telepítés" csomaglistát is.

Installation
-------------

You need to install python-apt package for python2.x or python3.x. On
Ubuntu you need::

    sudo apt-get install python-apt
    or
    sudo apt-get install python3-apt

Get the program from github.com, and run the packet_peak.py script with
python(2) or python3. On Ubuntu::

    sudo apt-get install git
    git clone git://github.com/taxy/packet-peak.git
    cd packet-peak
    python packet_peak.py
