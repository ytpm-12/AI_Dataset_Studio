from datetime import datetime, timedelta
from pathlib import Path
import random

import numpy as np
import pandas as pd


NB_LIGNES = 1000
NOMS_PRODUITS = ["A-100", "B-200", "C-300", "D-400", "E-500", "F-600", "G-700"]
CATEGORIES = [
    "Electroménager",
    "Informatique",
    "Maison",
    "Jardin",
    "Sport",
    "Jouets",
    "Automobile",
]
STATUTS = ["Expédié", "En préparation", "Livré", "En attente", "Annulé", "Retourné"]
DATE_DEBUT = datetime(2023, 1, 1)
FORMATS_DATE = ["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"]
FICHIER_SORTIE = Path(__file__).with_name("dataset_ventes_sale.csv")


random.seed(42)

data = {
    "Transaction_ID": list(range(1001, 1001 + NB_LIGNES)),
    "Product_Code": [],
    "Category": [],
    "Quantity": [],
    "Unit_Price": [],
    "Order_Date": [],
    "Status": [],
    "Discount (%)": [],
    "Notes": [],
}

for index in range(NB_LIGNES):
    code = random.choice(NOMS_PRODUITS)
    if random.random() < 0.1:
        code = " " + code + " "
    data["Product_Code"].append(code)

    data["Category"].append(random.choice(CATEGORIES))

    quantity = random.randint(1, 10)
    if random.random() < 0.03:
        quantity = -quantity
    if random.random() < 0.02:
        quantity = random.choice([999, 1111])
    data["Quantity"].append(quantity)

    if random.random() < 0.06:
        data["Unit_Price"].append(np.nan)
    else:
        price = round(random.uniform(5.0, 500.0), 2)
        if random.random() < 0.03:
            price *= 100
        data["Unit_Price"].append(price)

    if random.random() < 0.08:
        data["Order_Date"].append("date inconnue")
    else:
        random_date = DATE_DEBUT + timedelta(days=random.randint(0, 365 * 2))
        date_format = random.choice(FORMATS_DATE)
        data["Order_Date"].append(random_date.strftime(date_format))

    status = random.choice(STATUTS)
    if random.random() < 0.15:
        status = status.lower()
    if random.random() < 0.05:
        status += " "
    data["Status"].append(status)

    if random.random() < 0.07:
        data["Discount (%)"].append(np.nan)
    elif random.random() < 0.04:
        data["Discount (%)"].append("10%")
    elif random.random() < 0.03:
        data["Discount (%)"].append(".5")
    else:
        data["Discount (%)"].append(round(random.uniform(0, 0.3), 2))

    if random.random() < 0.12:
        data["Notes"].append("")
    else:
        data["Notes"].append(f"Commande standard - lot {random.randint(1, 20)}")

dataset = pd.DataFrame(data)

for duplicate_index in range(8):
    source_index = random.randint(0, NB_LIGNES - 1)
    duplicate_row = dataset.loc[source_index].copy()
    duplicate_row["Transaction_ID"] = 9000 + duplicate_index
    dataset.loc[len(dataset)] = duplicate_row

dataset = dataset.sample(frac=1, random_state=42).reset_index(drop=True)
dataset.to_csv(FICHIER_SORTIE, index=False)

print(f"Fichier '{FICHIER_SORTIE.name}' généré avec {len(dataset)} lignes.")
print(dataset.head(10))
