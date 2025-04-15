from enum import Enum

class CategoryType(Enum):
    income = "income"
    expense = "expense"

print(CategoryType._value2member_map_)
