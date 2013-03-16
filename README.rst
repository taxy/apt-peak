packet-peak project
===================

package-peak
-------------

Nagyon hasonlít a deborphan-hoz, lényegében a koncepció tovább fejlesztése python-apt alapokon.
A deborphan csak egyszerűen kilistázza azokat a csomagokat amiktől egyetlen másik csomag sem függ. Ezek a csomagok a függőségi rendszer csúcsán vannak. Néha az ajánlott függőségek kört alkotnak a kötelező függőségekkel együtt. Az ilyen csomagokat a deporphan nem listázza ki, pedig ha nem szándékosan telepítettük őket, akár feleslegesek is lehetnek. Ez az amit ez a program még külön figyel, és ha ilyen kört talál, akkor a kötelező függőségek csúcsát(mert azok nem alkothatnak kört természetesen) teszi be a listába. Így egy jó kivonatot kaphatunk a rendszerünkben található csomagokról. Általában ezt arra lehet használni, hogy kiszelektáljuk a szemetet, de készíthetünk a segítségével "tipikus telepítés" csomaglistát is.

Installation
-------------

You need to install python-apt package for python2.x or python3.x. On
Ubuntu you need::

    sudo apt-get install python-apt
    or
    sudo apt-get install python3-apt

Get the program from github.com, and run the package_peak.py script with
python(2) or python3. On Ubuntu::

    sudo apt-get install git
    git clone git://github.com/taxy/packet-peak.git
    cd packet-peak
    ./package_peak.py

Example to use::

    ./package_peak.py > current.list
    diff -u my_confirmed_packages.list current.list
