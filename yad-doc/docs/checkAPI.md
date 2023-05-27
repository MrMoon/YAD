# CheckAPI

## What is CheckAPI? 
CheckAPI tool checks if the compare.cpp file follows source.cpp file in term of functions and classes signatures.
It can chekc if both codes are exactly the same or if compare.cpp has at least all the functions and classes that are in source.cpp 

## Commands:

`CheckAPI source.cpp compare.cpp exactly` -check if both files have the same functions and classes

`CheckAPI source.cpp compare.cpp at_least` -check if compare.cpp have at least all the functions and classes that are in source.cpp


## Output options
<h3> <strong> -n: </strong> </h3> 
the default option, outputs the number of violations. 

<h3> <strong> -v:  </strong> </h3>
outputs a list of violations. 