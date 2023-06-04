import setuptools

setuptools.setup(
    name="causal_rl",
    version="0.0.1",
    description="Causal Question Answering on Knowledge Graphs with Reinforcement Learning.",
    packages=setuptools.find_packages(),
    install_requires=[
       'aiohttp==3.8.3',
       'bidict>=0.22.0',
       'networkx>=2.8.7',
       'pandas>=1.5.2',
       'wandb>=0.13.9',
       'nltk>=3.7',
       'torch>=1.12.1',
       'tabulate>=0.9.0',
       'matplotlib>=3.6.3',
       'scikit-learn>=1.2.1',
       'datasets>=2.9.0',
       'transformers>=4.23.1',
       'sentencepiece>=0.1.97',
       'optuna>=3.1.1',
    ],
    python_requires='>=3.9',
)
