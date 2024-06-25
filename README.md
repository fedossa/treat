## The TRR 266 Template for Reproducible Empirical Accounting Research 

This repository provides an infrastructure for open science oriented empirical projects. It is targeted to the empirical accounting research crowd. It features a toy project exploring discretionary accruals of U.S. public firms and requires access to U.S. Compustat data via WRDS.

But even if you do not care about discretionary accruals (who wouldn't?) or do not have WRDS access, its code base should give you a feel on how the template is supposed to be used and how to structure a reproducible empirical project.

The default branch, `only_python`, is a stripped down version of the template that only contains Python workflow. The `main` branch contains both the R and Python workflows and is a work in progress.


### Where do I start?

You start by setting up few tools on your system.

- If you are new to Python, we recommend that you follow the [Real Python installation guide](https://realpython.com/installing-python/){target="_blank"} that gives a good overview of how to set up Python on your system.

- Additionally, you will also need to setup an Integrated Development Environment (IDE) or a code editor. We recommend using VS Code, please follow the ['Getting started with Python in VS Code Guide'](https://code.visualstudio.com/docs/python/python-tutorial){target="_blank"}.

- You wll also need [Quarto](https://quarto.org/){target="_blank"}, a scientific and technical publishing system. Please follow the ['Quarto installation guide'](https://quarto.org/docs/get-started/){target="_blank"} to install Quarto on your system.

- Finally, you will also need to have `make` installed on your system, if you want to use it. For Linux users this is usually already installed. For MacOS users, you can install `make` by running `brew install make` in the terminal. For Windows users, there are few options to install `make` and they are dependent on how you have setup your system. For example, if you have installed the Windows Subsystem for Linux (WSL), you can install `make` by running `sudo apt-get install make` in the terminal. If not you are probably better of googling how to install `make` on Windows and follow a reliable source.

If you are new to scientific computing, we suggest that you also pick up a reference from the list below and browse through it. The [Gentzkow and Shapiro (2014) paper](https://web.stanford.edu/~gentzkow/research/CodeAndData.pdf) is a particularly easy and also useful read. 

Then browse around the repository and familiarize yourself with its folders. You will quickly see that there are three folders that have files in them:

- `config`: This directory holds configuration files that are being called by the program scripts in the `code` directory. We try to keep the configurations separate from the code to make it easier to adjust the workflow to your needs.

- `code`: This directory holds program scripts that are being called to download data from WRDS, prepare the data, run the analysis and create the output files (a paper and a presentation, both PDF files).

- `data`: A directory where data is stored. You will see that it again contains sub-directories and a README file that explains their purpose. You will also see that in the `external` sub-directory there are two data files. Again, the README file explains their content.

- `doc`: Here you will find two Quarto files containing text and program instructions that will become our paper and presentation, by rendering them through the R markdown process and LaTeX.

- `info`: This is a folder that can store additional documentation. In our case you will find a RMarkdown file that introduces our TRR 266-themed ggplot theme.

You also see an `output` directory but it is empty. Why? Because you will create the output locally on your computer, if you want.


### How do I create the output?

Assuming that you have WRDS access, Vs Code and make installed, this should be relatively straightforward.

1. Click on the `Use this template` button on the top right of the repository and choose `Create a new repository`. Give the repository a name, a description and choose whether it should be public or private. Click on `Create repository`.
2. You can now clone the repository to your local machine. Open the repository in Vs Code and open a new terminal.
3. It is advisable to create a virtual environment for the project. You can do this by running `python -m venv venv` in the terminal. This will create a virtual environment in the `venv` directory. You can activate the virtual environment by running `source venv/bin/activate` on MacOS or Linux or `.\venv\Scripts\activate` on Windows. You can deactivate the virtual environment by running `deactivate`.
4. With an active virtual environment, you can install the required packages by running `pip install -r requirements.txt` in the terminal. This will install the required packages for the project.
5. Copy the file _secrets.env to secrets.env in the project main directory. Edit it by adding your WRDS credentials. 
6. Run 'make all' either via the console. 
7. Eventually, you will be greeted with the two files in the output directory: "paper.pdf" and "presentation.pdf". Congratulations! You have successfully used an open science resource and reproduced our "analysis". Now modify it and make it your own project!

### OK. That was fun. Bot how should I use the repo now?

The basic idea is to clone the repository whenever you start a new project. If you are using GitHub, the simplest way to do this is to click on "Use this Template" above the file list. Then delete everything that you don't like and/or need. Over time, as you develop your own preferences, you can fork this repository and adjust it so that it becomes your very own template targeted to your very own preferences.


### For TRR 266 Members: What else is in there for you?

This repository contains three files that TRR members that use R might find particularly useful. The file `code/R/theme_trr.py` features a ggplot theme that makes it easy to generate visuals that comply to the TRR 266 style guide. But ggplot in python is not yet polished and does not have the same level of quality as in R. The RMarkdown file in `info` takes you through the process. With the `doc/beamer_theme_trr266.sty` you can beef up your Quarto based beamer presentations to our fancy TRR design. Finally, the file `code/R/pull_wrds_data.py` might be useful if you want to learn how to download WRDS data directly from python.


### Why do you do abc in a certain way? I like to do things differently!

Scientific workflows are a matter of preference and taste. What we present here is based on our experiences on what works well but this by no means implies that there are no other and better ways to do things. So, feel free to disagree and to build your own template. Or, even better: Convince us about your approach by submitting a pull request!


### But there are other templates. Why yet another one?

Of course there are and they a great. The reason why we decided to whip up our own is that we wanted a template that also includes some of the default style elements that we use in our collaborative research center [TRR 266 Accounting for Transparency](https://accounting-for-transparency.de). And we wanted to have a template that is centered on workflows that are typical in the accounting and finance domain. Here you go.


### Licensing

This repository is licensed to you under the MIT license, essentially meaning that you can do whatever you want with it as long as you give credit to us when you use substantial portions of it. What 'substantial' means is not trivial for a template. Here is our understanding. If you 'only' use the workflow, the structure and let's say parts of the Makefile and/or the README sections that describe these aspects, we do not consider this as 'substantial' and you do not need to credit us. If, however, you decide to reuse a significant part of the example code, for example the code pulling data from WRDS, we think that giving credit would be appropriate.

In any case, we would love to see you spreading the word by adding a statement like 

```
This repository was built based on the ['treat' template for reproducible research](https://github.com/trr266/treat).
```

to your README file. But this is not a legal requirement but a favor that we ask 😉.


### References

These are some very helpful texts discussing collaborative workflows for scientific computing:

- Christensen, Freese and Miguel (2019): Transparent and Reproducible Social Science Research, Chapter 11: https://www.ucpress.edu/book/9780520296954/transparent-and-reproducible-social-science-research
- Gentzkow and Shapiro (2014): Code and data for the social sciences:
a practitioner’s guide, https://web.stanford.edu/~gentzkow/research/CodeAndData.pdf
- Wilson, Bryan, Cranston, Kitzes, Nederbragt and Teal (2017): Good enough practices in scientific computing, PLOS Computational Biology 13(6): 1-20, https://doi.org/10.1371/journal.pcbi.1005510


