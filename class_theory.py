# import matplotlib.pyplot as plt
#
# class Point:
#     def __init__(self,  x, y):
#         self.x = x
#         self.y = y
#
#     def __add__(self, other):
#         if isinstance(other, Point):
#             x = self.x + other.x
#             y = self.y + other.y
#             return Point(x, y)
#         else:
#             x = self.x + other
#             y = self.y + other
#             return Point(x, y)
#
#     def plot(self):
#         plt.scatter(self.x, self.y)
#
#
# a = Point(0, 2)
# d = a + 5
#
# print(d.x, d.y)


## Multiple Classes
# class Student:
#     def __init__(self, name, age, grade):
#         self.name = name
#         self.age = age
#         self.grade = grade # 0-100
#
#     def get_grade(self):
#         return self.grade
#
# class Course:
#     def __init__(self, name, max_students):
#         self.name = name
#         self.max_students = max_students
#         self.students = []
#
#     def add_student(self, student):
#         if len(self.students) < self.max_students:
#             self.students.append(student)
#             return True
#         return False
#
#     def get_avg_grade(self):
#         value = 0
#         for student in self.students:
#             value += student.get_grade()
#
#         return value / len(self.students)
#
#
# s1 = Student("Tim", 19, 95)
# s2 = Student("Bill", 19, 75)
# s3 = Student("Jill", 19, 65)
#
# course = Course("Sience", 2)
# course.add_student(s1)
# course.add_student(s2)
# print(course.add_student(s3))
# print(course.students)
# print(course.get_avg_grade())




## Inheritance

# class Pet:
#     def __init__(self, name, age):
#         self.name = name
#         self.age = age
#     def show(self):
#         print(f"I am {self.name} and I am {self.age} years old.")
#
#     def speak(self):
#         print("I do not know what to say")
#
# class Cat(Pet):
#     def __init__(self, name, age, color):
#         super().__init__(name, age)
#         self.color = color
#
#     def show(self):
#         print(f"I am {self.name} and I am {self.age} years old and I am {self.color}.")
#
#     def speak(self):
#         print("Meow")
#
# class Dog (Pet):
#     def speak(self):
#         print("Bark")
#
#
# class Fish(Pet):
#     pass
#
# p = Pet("Tim", 19)
# p.show()
# p.speak()
#
# c = Cat("Bob", 20, "brown")
# c.show()
# c.speak()
#
# d = Dog("Bill", 21)
# d.show()
# d.speak()
#
# f = Fish("amy", 22)
# f.show()
# f.speak()



# class Person:
#     number_of_people = 0 #common for each instance of class
#     GRAVITY = -9.8
#
#     def __init__(self, name):
#         self.name = name
#         Person.add_person()
#
#     @classmethod
#     def number_of_people_(cls):
#         return cls.number_of_people
#
#     @classmethod
#     def add_person(cls):
#         cls.number_of_people += 1
#
# p1 = Person("Tim")
# p2 = Person("Jim")
# print(Person.number_of_people_())



## Static Methods

# class Math:
#
#     @staticmethod #they do smth but they dont change anything
#     def add5(x):
#         return x + 5
#
#     @staticmethod
#     def add10(x):
#         return x +10
#
#     @staticmethod
#     def pr():
#         print("run")
#
# Math.pr()
# print(Math.add5(5))


##Dunder Methods (Double Underscore)
## специальные методы, которые начинаются и заканчиваются двойным подчеркиванием
## Магия заключатеся в том, что они не вызываются напрямую, их вызывает сам Python в определенных ситуациях:
## когда ты складываешь объекты, через +,
## пытаешься напечатать через print()
## или когда проверяешь доинну через len()

## Методы представления класса
## __str__(self): вызывается при print(obj) или str(obj).
## Предназначен для создания красивого описания пользователя

## __repr__(self): вызывается если просто вводишь имя объекта в консоли
## предназначено для разработчиков, поэтому должен быть максимально техническим

class Student:
    def __init__(self, name, major):
        self.name = name
        self.major = major

    def __str__(self):
        return f"Student {self.name} studying {self.major}"

    def __repr__(self):
        return f"student(name={self.name}, major={self.major}"

# student = Student("Ekaterina", "Management and Technology")
# print(student)


## Математические методы
## Позволяют использовать математические операторы с нашими объектами
## __add__(self, other): позволяет использовать знак +
## __sub__(self, other): позволяет использовать знак -
## __mul__(self, other): позволяет использовать *
## __truediv__(self, other): это обычное деление, результат всегда будет числом с плавающей точкой
## __mod__(self, other): остаток от деления %

## Методы сравнения
## Позволяют объектам понимать, какие из них больше, а какие меньше
## __eq__(self, other): для оператора ==
## __lt__(self, other): для оператора <
## __gt__(self, other): для оператора >

## Методы работы с коллекциями
## __len__(self): вызывает len(obj)
## __getitem__(self, key): позволяет обращаться к объекту по индексу

## Управление жизненным циклом
## __init__(self,..): вызывается при создании
## __del__(self): вызывается когда объект удаляется из памяти


#
# class Course:
#     total_courses = 0
#     def __init__(self, name, ects):
#         self.name = name
#         self._ects = ects
#         Course.add_course()
#
#     def __str__(self):
#         return f'Course {self.name} gives {self._ects} ECTS'
#
#     def __add__(self, other):
#         if isinstance(other, Course):
#             new_name = f"{self.name} & {other.name}"
#             return Course(new_name, self._ects + other._ects)
#         return NotImplemented
#
#     def __gt__(self, other):
#         if self._ects > other.ects:
#             return True
#         else:
#             return False
#
#     @property
#     def ects(self):
#         return self._ects
#
#     @ects.setter
#     def ects(self, value):
#         if value <= 0:
#             print("ERROR")
#         else:
#             self._ects = value
#
#     @classmethod
#     def add_course(cls):
#         cls.total_courses += 1
#
#
#
#
# c = Course("Python", 5)
# print(c.ects)    # Увидишь сообщение геттера
# c.ects = -5      # Увидишь ошибку сеттера
# c.ects = 10      # Увидишь, что значение поменялось
# print(c.ects)


# class UniversityCourse:
#     def __init__(self, name, ects):
#         self.name = name
#         self._ects = ects
#
#     def __str__(self):
#         return f"University course {self.name} {self._ects} ects"
#
#     @property
#     def ects(self):
#         return self._ects
#
#
# c = UniversityCourse(name="University Course", ects=6)
# c.ects = 8


class DataProject:
    def __init__(self, name):
        self.name = name

    def report(self):
        return f"Report for the project {self.name}"

class MLProject(DataProject):
    def __init__(self, name, model_type):
        super().__init__(name)
        self.model_type = model_type

    def report(self):
        return f"Report for the project {self.name}. Used model {self.model_type}"

p = MLProject("Customer Churn", "XGBoost")
print(p.report())