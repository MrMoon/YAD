# CheckAPI

## What is CheckAPI? 
CheckAPI tool checks if the source.cpp file follows the compare.cpp file in term of functions and classes signatures.
It can chekc if both codes are exactly the same or if source.cpp has at least all the functions and classes that are in compare.cpp 

## Commands:

`CheckAPI source.cpp compare.cpp exactly` -checks if both files have the same functions and classes

`CheckAPI source.cpp compare.cpp at_least` -checks if source.cpp have at least all the functions and classes that are in compare.cpp


## Output options
<strong> -o </strong> followed by either n or v (not case sensitive).\n
<strong>n</strong>: number of violation (default option)\n
<strong>v</strong>: verbose, list of violations with a minor explanation.\n

### Example command with option:
`CheckAPI source.cpp compare.cpp exactly -o v`
