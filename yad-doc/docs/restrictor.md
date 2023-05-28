# Restrcitor

## What is Restrictor? 
The Restrictor CLI tool allows the user to restrict the use of certain elements defined in a restrictions file such as libraries, keywords, global variables, extra functions, visibility of functions, recursion and iteration. 

## Commands
` restrict source.cpp restrictions.yaml` -restrictions.yaml is a yaml file that contains different restrictions and criterias  
` restrict source.cpp criteria restriction "to_be_restricted"`
    
    example:
    restrict source.cpp library at_least "iostream algorithms math"
    
    -check that libraries iostream, algorithm, and math are included inside source.cpp

## How does it work?
The user will create a yaml file to include all the restrictions to be checked, followed by a restriction of 3 types being one of the following:

- <strong>at_least:</strong> at least all the given appears in source.cpp, source.cpp can have more.

- <strong>exactly:</strong> source.cpp contains exactly the given.

- <strong>forbidden:</strong> source.cpp can't have any of the given.

There are 7 supported criteria which are:

Libraries, Keyword, Classes, Functions, Public Functions, Private Functions and Protected Functions.

<div class="bs-callout bs-callout-warning">
  <h4>Note</h4>
  For more explanation check the example section.
</div>

## Error Scenarios:
<strong> yaml file with syntax error: </strong>
<h6> for example if the yaml file contained "libary" instead of "library", it will compile but withot processing the library field </h6>

<strong> yaml file with logical error: </strong>
<h6> for example if the yaml file contained a keyword with "exactly" restriction and after that the same keyword with "forbidden" restriction, the last restriction will be applied. </h6>

## Output options
<strong> -n: </strong> 
the default option, outputs the number of violations. 

<strong> -v: </strong> outputs a list of violations. 

## Yaml File Structur:
the Yaml file consists of:

- <strong> Criteria: </strong>  <h6> libraries, keywords, classes, functions, public functions, private functions or protected Functions.</h6>
    For each criteria:

    - <strong> Restriction: </strong>
    <h6> at_least, exactly, or forbidden</h6>
    - <strong> Scope: </strong> 
        - <h6> choose the scope of restriction, such as "int functionC(int, int)" </h6>
        - <h6> default value of scope is global. </h6>
    - <strong> Names: </strong>
    <h6> specify what you want to restrict

## Example
