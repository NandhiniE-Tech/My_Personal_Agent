# pip install exa-py
from exa_py import Exa  #pip install numba exa to install exa-py not eror sorted still error.  
exa = Exa(api_key = "c74e3a1d-0d67-468d-9f8d-417c3c629214")
result = exa.search_and_contents(
    "find blog posts about AGI",
    text = { "max_characters": 1000 }
)
print(result)