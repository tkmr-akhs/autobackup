# Overview
This is a program for specifying a directory and automatically backing up the files under the directory.

# DEMO
```txt
C:\work>tree /f "C:\TargetDir"
├─testdir1
│      testfile1.txt
│
└─testdir
       testfile2.txt

C:\work>.\autobackup.bat

C:\work>tree "C:\TargetDir"
├─testdir1
│   │  testfile1.txt
│   │
│   └─.old
│      testfile1_2023-01-21_0000.txt
│
└─testdir
    │  testfile2.txt
    │
    └─.old
           testfile2_2023-01-21_0000.txt
```

# Usage
Configuration is done by creating a `cnf/my_settings.toml` file.

It is recommended that you do not change `cnf/defaults.toml`. If you want to change the default settings, override it with `my_settings.toml`.

Specify the directory where you want automatic backups to be performed as follows:
```toml
[[targets]]
path = 'C:\TargetDir'
catch_regex = '.*\.txt'
ignore_regex = ''
catch_hidden = false
catch_link = false

[[targets]]
path = 'C:\TargetDir2'
catch_regex = '.*\.html'
ignore_regex = ''
catch_hidden = false
catch_link = false
``` 
