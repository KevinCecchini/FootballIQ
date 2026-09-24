# FootballIQ ⚽

FootballIQ is a football decision-intelligence project designed to evaluate passing decisions using tracking data, contextual passing options and machine learning.

Rather than evaluating only whether a pass was completed, FootballIQ asks a different question:

> Given the game state and the available passing options, how good was the player's decision?

## Project Objective

The project reconstructs real possession states and compares the option actually selected by the ball carrier with the alternative passing options available at that moment.

Each decision is represented through contextual passing-option information including:

- Expected pass completion (xPass)
- Expected threat (xThreat)
- Passing option score
- Actual selected receiver

Additional spatial features such as pass distance, forward progression,
defender proximity and passing-lane obstruction were explored during
feature-engineering development.

The project quantifies the gap between the option selected by the player and the highest-value alternative estimated by the model.

## Data

The project uses the SkillCorner Open Data dataset, which provides broadcast tracking and Game Intelligence data for professional football matches.

Data source:

SkillCorner Open Data  
https://github.com/SkillCorner/opendata

Raw tracking data is not included in this repository.

## Methodology

The pipeline includes:

1. Tracking-data ingestion
2. Player and team metadata mapping
3. Reconstruction of possession states
4. Identification of passing options
5. Spatial feature engineering
6. Integration of SkillCorner xPass and xThreat metrics
7. Machine-learning modelling of passing decisions
8. Comparison between selected and alternative options
9. Player-level decision analysis

## Machine Learning

A Logistic Regression model is used as the initial interpretable baseline for estimating:

`P(option selected | game state)`

Features include:

- `passing_option_score`
- `xpass_completion`
- `xthreat`

Decision-level train/test splitting is used to avoid leakage between passing options belonging to the same possession.

More advanced models can subsequently be compared against this baseline.

## FootballIQ Decision Value

A simple first decision-value formulation is:

`Expected Threat Value = xPass × xThreat`

For every possession, FootballIQ compares:

- the value of the selected option
- the highest-value available alternative

The difference is defined as the:

**Decision Gap**

A smaller Decision Gap indicates that the selected action was closer to the highest-value option according to the model.

This is a model-based estimate rather than an objective definition of the "correct" football decision.

## Repository Structure

```text
FootballIQ/
│
├── notebooks/
│   └── 01_data_exploration.ipynb
│
├── src/
│   ├── tracking_utils.py
│   ├── feature_engineering.py
│   ├── event_processing.py
│   └── pipeline.py
│
├── data/
│   └── processed/
│       ├── footballiq_decisions.csv
│       ├── footballiq_decision_summary.csv
│       └── footballiq_player_summary.csv
│
├── outputs/
│   └── figures/
│
├── README.md
├── requirements.txt
└── .gitignore
```

## Tech Stack

- Python
- Pandas
- NumPy
- Matplotlib
- Scikit-learn
- JupyterLab

## Current Status

FootballIQ currently includes an end-to-end MVP pipeline for:

- processing real football possession events
- identifying available passing options
- constructing decision-level features
- modelling observed passing choices
- comparing chosen actions with alternative options
- generating player-level decision summaries

## Outputs

The project produces:

- decision-level passing-option datasets
- selected-vs-alternative comparisons
- expected threat-based decision values
- Decision Gap metrics
- player-level decision summaries
- tactical decision visualisations

## Future Development

Potential extensions include:

- XGBoost / LightGBM models
- SHAP explainability
- richer pitch-control features
- player velocity and movement features
- improved pressure modelling
- larger multi-match training datasets
- interactive Streamlit decision explorer
- player and team decision profiles

## Limitations

FootballIQ estimates decision quality using observable tracking and event data.

The model does not directly observe factors such as:

- tactical instructions
- player vision and perception
- communication between teammates
- fatigue
- body orientation in all situations
- coaching objectives
- contextual match strategy

Therefore, the highest-value option identified by the model should be interpreted as a model-based estimate rather than the objectively correct football decision.

## Data Attribution

Tracking and Game Intelligence data used in this project are provided by SkillCorner through their Open Data initiative.

SkillCorner Open Data:  
https://github.com/SkillCorner/opendata
