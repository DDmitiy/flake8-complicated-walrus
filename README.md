# flake8-complicated-walrus

This *Flake8* plugin for checking complicated assignment expressions.
There are 3 levels for this linter:
1. *restrict-all* - **restrict** use assignment expressions **in any case**
2. *restrict-complicated* - **restrict** use assignment expressions **in complex if conditions**
3. *allow-all* - **allow** use assignment expressions **in any case**

# Quick Start Guide

1. Install ``flake8-complicated-walrus`` from PyPI with pip::

        pip install flake8-complicated-walrus

2. Configure a mark that you would like to validate::

        cd project_root/
        vi setup.cfg

3. Add to file following: 
   
        [flake8]  
        restrict-walrus-level = restrict-complicated  

3. Run flake8::

        flake8 .

# flake8 codes

   * FCW100: You cannot use assignment expression.
   * FCW200: You cannot use assignment expression in complicated if statements.

# Settings

**restrict-walrus-level**  
It specifies restrict level for linting your code. 
