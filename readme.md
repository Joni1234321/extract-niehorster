# Main files
## single.py 
1. Command
# multi.py
1. .org file
2. .json file
# main.py 
1. Link to niehorster
2. Name
3. Country
4. Year

# Commands
## Command Syntax
name last_equipment n_sub_units hq_equipment notes n

1. **name** is a string that contains two types, the last string is the size of the unit, the first is the type [unknown]
2. **last_equipment** is the equipment of the lowest level unit [Ø]
3. **n_sub_units** is the amount of sub units each level down, write 0 if there is no units
4. **hq_equipment** is the equipment in each hq give 0 if there is no hq
5. **notes** is some random string you always can write
6. **n** is the amount of units

## Equipment strings syntax
Equipment string

Default first item in each level is the amount of men

Each level is split by underscore '_'  
*Example: 2_3 means 2 men in unit level, and 3 men in level under*

Each item is split by comma ','  
*Example: 2,horse:3,truck:4 means 2 men and 3 horses and 4 trucks*

Each item is given its count by colon ':'  
*Example: 2,horse:3,truck:4 means 2 men and 3 horses and 4 trucks*


## File type
**.org** contains the list of commands  
**.json** is the org in json format
### .org Syntax
Give name and link of unit, name is ignored and only used as a way to comment files.
Link is used to insert into the given link in the .json file, end with colon  
*example: Infantry Regiment,44_rd_inf-rgt:*

# Folders
### results 
Contains the .org and .json files  
Each table has 3 files associated files
1. **.json** file as a direct copy of niehorster.com, 
2. **.org** file with the rest of organization that was not copied
3. **_final.json** file with final version of the organization
### scripts
Contains .abbr files used to convert abbreviations into the same full words. ( only works with single words, no lexer implemented yet)
### niehorster
A copy of niehorster ussr website, for testing purposes