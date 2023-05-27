# CommentController

## Whats CommentController:
CommentControl tool allows the user to control comments by extracting or removing comments, or by commenting out certain classes or functions.

## Commands:
### Extract Comments:
This tool will extract all the comments from a C++ file and output the comments into the file of your choosing.

`commentCtrl extract source.cpp "function prototype"`

### Extract Header:
This tool will extract all header comments from a C++ file and output the comments into the file of your choosing.

`commentCtrl header source.cpp "function prototype"`

### Delete Comments:
This tool will delete all the comments from a .cpp or .h file and output the source code into the file of your choosing.

`commentCtrl delete source.cpp "function prototype"`

### Comment Out Function:
This tool will comment out a function implementation from a C++ file using a function prototype.

`commentCtrl commentOutFunction source.cpp "function prototype"`

### Comment Out Class:
This tool will comment out a Class implementation from a C++ file.

`commentCtrl commentOutClass source.cpp "class class-name"`

By default, it only comments out the class with its member functions. Adding the option '-all' comments out the all its dependent classes:

`commentCtrl commentOutClass source.cpp "class class-name" -all True`

## Error Scenarios:
- Function doesn't exist in source.cpp 

<div class="bs-callout bs-callout-warning">
  <h4>Note</h4>
  for reference on how to write functions' parameters, please check <href a= "reference.md"> the reference page
</div>


