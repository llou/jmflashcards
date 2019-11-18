.. image:: http://orangeorapple.com/Flashcards/images/WebIcon70.png 

============
jmflashcards
============
-----------------------------------
A Flashcards Deluxe cards processor
-----------------------------------

.. image:: https://travis-ci.com/llou/jmflashcards.svg?branch=master

`Flashcards Deluxe`_ is an app for Android_ and iOs_ devices that helps in the
memorization process using a well known technique called *flash cards*. It is a
very nice app with a lot of features that enrich the studying process. 

.. _`Flashcards Deluxe`: http://orangeorapple.com/Flashcards/
.. _Android : https://play.google.com/store/apps/details?id=com.orangeorapple.flashcards&hl=en
.. _iOs: https://apps.apple.com/us/app/flashcards-deluxe/id307840670

The problem I found with the app is the method of creating and uploading the
cards into the devices was a little bit annoying. As I needed to create a large
number of cards of multiple disciplines and some included math symbols and
other images, I decided to automate the building of the card decks.

This is done using the well known format YaML_ that contains the list of cards
each one with two key value entry one with the question and another one with
the answer. 

.. _YaML: https://en.wikipedia.org/wiki/YAML

.. TODO Example of card, mirar la forma de insertar codigo

.. code:: yaml

  - question: How you set up a function in javascript to be run after certain
              time?
    answer: With <i>setTimeout(function, time)</i>
  - question: How you set up a function in javascript that runs in periods
              of time?
    answer: With <i>setInterval(function, time)</i>
    

The program works syncronizing two directories, one with the cards source and
another one inside a cloud storage system directory called *Flashcards deluxe*
where the cards definition are stored ready to be picked from the app.

Installation
------------
The program can be installed in \*nix systems running the ``setup.py install``
command as root. It's depedencies are listed in the ``requirements.txt`` file.

Configuring the app
-------------------
The key words used in the definition files for *question* and *answer* can be
changed with a configuration file stored in the users
``~/.config/jmflashcards/config.yaml`` directory, so it can be used in multiple
languajes, the location of the *input* and *output* directories can be set from
there too. The file is in *YaML* *key-value* format and the entries accepted
are:

* **input_dir**: root of the cards tree.

* **outpu_dir**: directory where the cards are placed to be picked by the
  mobile app.

* **question_keys**: This is a YaML list of valid keys to be used to identify
  the front side of the card.

* **answer_keys**: This is a YaML list of valid keys to be used to identify
  the back side of the card.


Creating the repository
-----------------------
The repository is a *tree* of directories having the root in the *input*
directory. Each *leaf* directory defines a flashcard with its name and it must
contain at least one file called ``flashcards.yaml`` where the cards are
defined. There can be  other files with images and sounds that can be
referenced in the definition file.

Card syntax
-----------
The syntax of the file is simple, a list of ``question:`` and ``answer:``
pairs or whatever you have chosen to name the cards. Then 

* If you start writting text after the colon it is a text entry that can be
  formated using the `Flashcards deluxe syntax`_. The text can be extended to
  mutiple lines using the YaML_ syntax.

.. _`Flashcards deluxe syntax`: http://orangeorapple.com/Flashcards/

* If you want to include an image or sound you have to put the ``~`` after de
  colon followed with the name of the image file stored within the definition
  directory.

* If you want to include a mathematical expression start with a ``$`` simbol and
  then the expression using te `latex syntax`_.

.. _`latex syntax`: https://en.wikibooks.org/wiki/LaTeX/Mathematics

Syncronization
--------------
The app is ran with the command ``jmflashcards`` and crawls the definition tree
processing each one of the files, to see if it has to *render* the card it
compares the timestamps of the original card and the renderd one and if the
first is newer it overwrites the old one.








