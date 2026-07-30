from dataclasses import dataclass

@dataclass
class  Ingredient:

    id: int
    inci_name : str
    chinese_name : str
    category : str
    functions : list[str]
    suitable_skin_types : list[str]
    avoid_skin_types : list[str]
    risk_level : str
    description : str


    