# Causal LM (Next-Token Prediction)

This is the base self-supervised training method used in modern decoder-only transformers (GPT, Llama, etc.).

## Method Description

Causal Language Modeling trains the model to predict the next token in a sequence given all previous tokens.  
It is the standard pre-training objective for autoregressive large language models.

## Key Characteristics

- Self-supervised (no labels required)
- Autoregressive (causal attention mask)
- Produces the classic "spiral galaxy" visualization in the Niagara universe
- Foundation for all other decoder-based methods

## Usage

This method is loaded automatically when VERSAI_TRAINING_STYLE=causal_lm
