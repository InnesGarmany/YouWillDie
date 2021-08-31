priceOfDrinks = {
    "wine": {
        "price": 300,
        "types": ["shiraz","blanc"]
    },
    "lager": {
        "price": 250,
        "types": ["tennents", "stella"]
    },
    "cocktail": {
         "price": 500,
         "types": ["negroni", "gin & tonic"]
    }
}

print(priceOfDrinks.get("wine").get("types","No price")[1])
