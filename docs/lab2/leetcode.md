# [Remove Duplicates from Sorted Array II](https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/?envType=study-plan-v2&envId=top-interview-150)

## Решение

Для решения задачи используется метод двух указателей:

- Инициализируем два указателя: j для записи уникальных элементов с ограничением на два повторения.
- Проходим по массиву начиная с третьего элемента (индекса 2) и проверяем:
- Если текущий элемент не равен предыдущему элементу, записываем его на позицию j и увеличиваем j. 
- Если текущий элемент равен предыдущему, то проверяем, встречается ли этот элемент более двух раз подряд. Если нет, записываем его на позицию j и увеличиваем j.
- Возвращаем количество уникальных элементов в начале массива.
- 
## Код решения
```python
class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        if len(nums) <= 2:
            return len(nums)
    
        j = 1
        
        for i in range(2, len(nums)):
            if nums[i] != nums[j-1]:
                j += 1
                nums[j] = nums[i]
        
        return j + 1
```