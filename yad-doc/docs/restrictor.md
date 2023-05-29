# Restrcitor

## What is Restrictor? 
The Restrictor CLI tool allows the user to restrict the use of certain criterion or many criteria in a source file, the restriction follows one of three types of restrition explained below.

## Types of Restriction:
- <strong>at_least:</strong> must contain the search criterion in source.cpp, other components of the same criterion can exist.

- <strong>exactly:</strong> must contain the search criterion in source.cpp, other components of the same criterion must not exist (not available for keyword criterion, explained below).

- <strong>forbidden:</strong> must not contain the search criterion, other components of the same criterion can exist.

## How does a single criterion restriction work?
Each criterion has a unique character to use with the command, the characters are explained below, the output of the commands is True (following restriction) or False (not following restriction):

- <strong>l:</strong> used for restricting libraries, must input only the library name, this is the only criteria that doesn't allow scope definition (don't input #include).

- <strong>k:</strong> used for restricting keywords, this feature does an exact match search need so you need to input the exact keyword you are looking for (can be used to find recursion or iteration). <strong>Important note</strong>: preferably don't use global scope, specify a certain scope for accuracy.

- <strong>c:</strong> used for restricting classes, input class prototype.

- <strong>f:</strong> used for restricting functions without access types (functions outside of classes), input function prototype.

- <strong>a:</strong> used for restricting functions with their access types (Public/Protected/Private), input function access type followed by function prototype.

### Example Commands:
- <strong>l:</strong> `restrict l source.cpp exactly iostream` -Checking if only iostream exists in code (it must exist).

- <strong>k:</strong> `restrict k source.cpp at_least follow "int follow(int, int)"` -Checking recursion exists (it must exist).

- <strong>c:</strong> `restrict c source.cpp forbidden "class shape" global` -Checking if class shape exists in code (it must not exist).

- <strong>f:</strong> `restrict f source.cpp at_least "int follow(int, float)" global` -Checking if function int follow(int, float) exists (it must exist).

- <strong>a:</strong> `restrict a source.cpp exactly "float shape::area()" "class shape" private` -Checks if the only private function in class shape is area() (it must exist).

## How does many criteria restriction work?

- <strong>r:</strong> used for restricting source file according to a YAML restrictions file, the format of the restrictions file is explained in Restrictions File section found below.

### Many Criteria Command:

`restrict r source.cpp rules.YAML` -Returns the number of missing functions/classes following by the number of extra functions/classes.

### Output Options

This command includes an output option <strong>-o</strong>, the output option is follow by n (number of missing and extra functions) which is the default value or v (verbose, a list of violations with a simple explanation) both n and v are not case sensitive, an example command including v:

`restrict r source.cpp rules.YAML -o v` -Returns a list of violations with minor explanation.

### Restriction File Structur:
The restrictions file is a YAML file type, this file is required for the functionality of the many criteria command.

- <strong> Criteria supported: </strong>  <h6> libraries, keywords, classes, functions, public functions, private functions or protected Functions.</h6>
    For each criteria:
    
    - <strong> Restriction: </strong>
        - <h6> at_least </h6>
        - <h6> exactly </h6>
        - <h6> forbidden </h6>
    - <strong> Scope: </strong> 
        - <h6> Choose the scope of restriction, such as "int functionC(int, int)" </h6>
        - <h6> Default value of scope is global when left empty. </h6>
    - <strong> Names: </strong>
        - <h6> Specify what you want to restrict. </h6>

### Restrictions File Example
You can find the sample file in the GitHub files or below:

```
libraries:
  restriction: at_least
  scope: global
  names:
    - algorithm
    - iostream

keywords:
  restriction: exactly
  scope: int functionC(int, int)
  names:
    - functionC

classes:
  restriction: exactly
  scope: global
  names:
    - class test
    - class Aclass

functions:
  restriction: exactly
  scope: global
  names:
    - int functionA(int, int)
    - template <typename T> int functionD(T)
    - int * functionE(int, int)
    - int ** functionF(int, int)
    - int functionJ(int &)
    - int functionK(int *)

private_functions:
  restriction: exactly
  scope: global
  names:
    - int test::functionG(int, int) const
    - virtual void test::functionH()
    - static int test::functionI(int, int)
```

## Error Scenarios:
<strong> YAML file with syntax error: </strong>
<h6> For example if the yaml file contained "libary" instead of "library", restrictor will not check for libraries and return an answer as if the "library" criterion was empty.</h6>

<strong> YAML file with logical error: </strong>
<h6> For example if the yaml file contained a keyword with "exactly" restriction and after that the same keyword with "forbidden" restriction, the last occurance in the file will be applied.</h6>
