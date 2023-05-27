# Isolator

## What is Isolator? 
Isolator tool isolates the whole code from a given function or class inside destination code and replaces the isolated function or class from source code inside destination code.
It consists of two parts, IsolateFunction and IsolateClass.

## Commands:
### Isolate Function
` isolator isolateFunction source.cpp destination.cpp "function prototype" ` 
### Isolate Class 
` isolator isolateClass source.cpp destination.cpp "class  class-name" `

By default, it only isolates the class with its member functions. Adding the option '-all' also isolates all its dependent classes:

` isolator isolateClass source.cpp destination.cpp "class  class-name" -all True`

## How does it work?
First of all the desired function\class must have the same signature in both source and destination files, then Isolator will search for the desired function\class inside source.cpp and take a copy of it, after that it will search for the desired function\class inside destination.cpp.
    
## Where it will be inserted? 
### <strong> Isolate fucntion: </strong>

<strong> Non-member function: </strong>

Function's prototype will be inserted in the beginnig of the code, and function's implementation will be inserted at the end of the code.

<strong> Member function: </strong>

- The orginal function is implemented inside the class: 

    Function will be inserted at the end of the class.

- The orginal function is implemented inside the class: 

    Function's prototype will be inserted at the end of the class, and function's implementation will be inserted at the end of the code.

### <strong> Isolate Class:</strong>
<strong> Class found in destination code: </strong>
    
Original class will be commented and the copied class from source.cpp will be pasted in the exact place of the original class in detination.cpp

<strong> Class not found in destination.cpp: </strong>
    
The copied class from source.cpp will be pasted at the end of detination.cpp 

## Scenarios:
### Isolate Function:
Below are examples of how to write the function's parameter

<strong> Non-member Functions: </strong> 

- Normal Function: simply write the function prototype, such as: 
    - `"int sum(int , int)"`
- Template Function write the function prototype along with the template definition:
    - `"template <typename T> T myMax1(T &, T)"`

<strong> Member Functions: </strong>

- Normal & Template Fucntions: You need to add the name of the parent class:
    - `"template <typename T> T MyClass:: myMax2(T &, T)"`
    - `"void MyClass:: print()"` 
- Static: Write the static key word at the beginning of the prototype:
    - `"static void MyClass::eat()"`
- const: 
    - `"double MyClass:: getArea() const"` 
- virtual: 
    - `"virtual double MyClass:: getArea() const"`
- pure virtual:
    - `"virtual double MyClass:: getArea() const = 0"` 
- constructor: 
    - `"MyClass :: MyClass()"`
- initiaizer list:
    - `"MyClass :: MyClass(int, double, char) : myInt()"`
- copy constructor: 
    - `"MyClass :: MyClass(const MyClass&)"`
- destructor: 
    - `"MyClass :: ~MyClass()"`

### Isolate Class:

<strong> Class: </strong>

- isolate class with member functions only:

    - `isolator isolateClass source.cpp destination.cpp "class Animal"` 

- isolate class with all dependent classes:

    - `isolator isolateClass source.cpp destination.cpp "class Animal" -all true` 

<strong> Struct: </strong>

- isolate struct with member functions only:

    - `isolator isolateClass source.cpp destination.cpp "struct Node"` 

- isolate struct with all dependent classes:

    - `isolator isolateClass source.cpp destination.cpp "struct Node" -all true` 

