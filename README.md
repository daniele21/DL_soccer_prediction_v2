# Soccer Match Prediction

![Licence](https://img.shields.io/badge/Licence-MIT-orange)

Libraries: 

![Pytorch](https://img.shields.io/badge/Pytorch-1.8-brightgreen)
![Flask](https://img.shields.io/badge/Flask-2.0.1-brightgreen)
![Tkinter](https://img.shields.io/badge/Tkinter-0.1.0-brightgreen)
![Pandas](https://img.shields.io/badge/Pandas-1.2.4-brightgreen)

Dependences:

[![Python](https://img.shields.io/badge/Python-3.6-yellow)](https://github.com/daniele21/Genre_Detection/blob/master/dependences.md)

## Contents
- [Description](#description)
- [Dataset](#dataset)
- [Task](#task)
- [Solution](#solution)


------------------------

# Description
The idea is to create a custom **deep learning** algorithm for soccer match events, in particular the **double chances** events, that are *1X* and *X2*. This events represent respectively the cases of home team winning/drawing and away team winning/drawing.

**Goal**: Training a neural network able to predict with **high precision** the double chances in soccer matches and building up a **MLOps architecture**, based on **API**, able to manage the training/inference of model in a automatic way.


# Dataset
It was extracted from [football-data uk](https://www.football-data.co.uk/), which permits to access to many national data tournaments, fully updated after every match. This website provides free data and available to everyone. 

The given data contains many details for each match results: 
- *match data*
- *home team and away team*
- *final score*
- *half time score*
- *betting odds*
- *some match statistics (such as shots, corners, fouls, yellow/red card, etc...)*

All details of the given dataset are available [here](https://www.football-data.co.uk/notes.txt)

I use my model to train over the following national tournaments:
- Italy *(Serie A)*
- England *(Premier League, Championship)*
- Germany *(Bunsdesliga, Bundesliga 2)*
- Nederland *(Eredivisie)*
- Spain *(Liga, Liga 2)*
- France *(Ligue 1, Ligue 2)*
- Belgium *(Jupilier)*


# Task
Multi-variate Time-Series Classification

# Solution
The provided solution is divided in two part: the first one regards the **architecture** of the project and the second one is a technical part, related to the **deep learning model** for the event prediction

### Architecture
It is structred with Flask **API** on top that manage the possibilties of training and infering the DL model. Basing on **MLOps** theory, the training is triggered through some API, it chooses the best hyperparameters for that model and evaluate it. Finally set the model up to be processed. The prediction is also triggered through API.

### Model
I create a neural network model that consists on merging two neural network branches: the first one processes data **optimizing** the favourite chance for home team (**1X**) and the second one takes care of optimizig the favourite chance for away team (**X2**)

Two networks were tested for solving this problem:
- Each neural network branch is composed by **LSTM network Fully Convolutional**
- Each neural network branch is composed by **LSTM network Fully Connected**

The two branches are then concateneted. 

------------------------

#### Author
Daniele Moltisanti

[![Linkedin](https://img.shields.io/badge/Linkedin-Daniele%20Moltisanti-blue)](https://www.linkedin.com/in/daniele-moltisanti/)

[![Portfolio](https://img.shields.io/badge/Portfolio-Daniele%20Moltisanti-9cf)](https://daniele21.github.io)
