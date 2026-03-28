# Header Guardian, a C/C++ header guard creator and updater

This tool can be used to update C/C++ header guards, typically using the header file path to generate unique header guards for each header.


# Usage

 ```bash
$ header_guardian --help
usage: header_guardian [-h] (--input INPUT | -r DIR) [--output OUTPUT] [--prefix PREFIX] [--suffix SUFFIX] [--nameroot NAMEROOT]
                       [--create] [--width WIDTH] [--verbose] [--quiet]

Replace header guard with a path-based header guard (from nameroot). Assumes that the relevant preprocessor directives start at column
0 with no extra spacing.

options:
  -h, --help           show this help message and exit
  --input INPUT        Path to input header, or hyphen (-) for stdin (default: )
  -r DIR               Recursively process all .h, .H, .hpp, .HPP files from DIR (default: )
  --output OUTPUT      Path to output file, or hyphen (-) for stdout (default: -)
  --prefix PREFIX      Prefix to add to the filename guard name (default: )
  --suffix SUFFIX      Suffix to add to the filename guard name (default: )
  --nameroot NAMEROOT  Root directory for naming (default is cwd) (default: None)
  --create             Create a header guard if one does not already exist (default: False)
  --width WIDTH        Use a hash instead of text for long lines (default: 0)
  --verbose, -v
  --quiet, -q
```

# Example

Here are some header files without guards:

 ```bash
$ tree .
.
├── directory1a
│   └── directory2
│       └── directory3
│           └── directory4
│               └── directory5
│                   ├── func1.h
│                   └── func2.h
└── directory1b
    └── directory2
        └── directory3
            └── directory4
                └── directory5
                    ├── func3.h
                    └── func4.h

11 directories, 4 files

$ cat directory1a/directory2/directory3/directory4/directory5/func1.h 
void func1();

$ cat directory1a/directory2/directory3/directory4/directory5/func2.h 
void func2();

$ cat directory1b/directory2/directory3/directory4/directory5/func3.h 
void func3();

$ cat directory1b/directory2/directory3/directory4/directory5/func4.h 
void func4();
 ```

Updating guards fails because they do not exist:

 ```bash
$ header_guardian --nameroot . --input directory1a/directory2/directory3/directory4/directory5/func1.h --output directory1a/directory2/directory3/directory4/directory5/func1.h
Non-conforming file: directory1a/directory2/directory3/directory4/directory5/func1.h

$ echo $?
1

$ cat directory1a/directory2/directory3/directory4/directory5/func1.h
void func1();
 ```

Create guards, one at a time:

 ```bash
$ header_guardian --nameroot . --input directory1a/directory2/directory3/directory4/directory5/func1.h --output directory1a/directory2/directory3/directory4/directory5/func1.h --create
Non-conforming file: directory1a/directory2/directory3/directory4/directory5/func1.h
Creating new guard: directory1a/directory2/directory3/directory4/directory5/func1.h

$ header_guardian --nameroot . --input directory1a/directory2/directory3/directory4/directory5/func2.h --output directory1a/directory2/directory3/directory4/directory5/func2.h --create
Non-conforming file: directory1a/directory2/directory3/directory4/directory5/func2.h
Creating new guard: directory1a/directory2/directory3/directory4/directory5/func2.h

$ header_guardian --nameroot . --input directory1b/directory2/directory3/directory4/directory5/func3.h --output directory1b/directory2/directory3/directory4/directory5/func3.h --create
Non-conforming file: directory1b/directory2/directory3/directory4/directory5/func3.h
Creating new guard: directory1b/directory2/directory3/directory4/directory5/func3.h

$ header_guardian --nameroot . --input directory1b/directory2/directory3/directory4/directory5/func4.h --output directory1b/directory2/directory3/directory4/directory5/func4.h --create
Non-conforming file: directory1b/directory2/directory3/directory4/directory5/func4.h
Creating new guard: directory1b/directory2/directory3/directory4/directory5/func4.h

$ echo $?
0

$ cat directory1a/directory2/directory3/directory4/directory5/func1.h
#ifndef DIRECTORY1A_DIRECTORY2_DIRECTORY3_DIRECTORY4_DIRECTORY5_FUNC1_H
#define DIRECTORY1A_DIRECTORY2_DIRECTORY3_DIRECTORY4_DIRECTORY5_FUNC1_H

void func1();

#endif  // DIRECTORY1A_DIRECTORY2_DIRECTORY3_DIRECTORY4_DIRECTORY5_FUNC1_H

$ cat directory1b/directory2/directory3/directory4/directory5/func4.h
#ifndef DIRECTORY1B_DIRECTORY2_DIRECTORY3_DIRECTORY4_DIRECTORY5_FUNC4_H
#define DIRECTORY1B_DIRECTORY2_DIRECTORY3_DIRECTORY4_DIRECTORY5_FUNC4_H

void func4();

#endif  // DIRECTORY1B_DIRECTORY2_DIRECTORY3_DIRECTORY4_DIRECTORY5_FUNC4_H
 ```

Update directory1a headers automatically, adding a guard macro name prefix:

 ```bash
$ header_guardian --prefix SYS1_ --nameroot . -r directory1a

$ echo $?
0

$ cat directory1a/directory2/directory3/directory4/directory5/func2.h 
#ifndef SYS1_DIRECTORY1A_DIRECTORY2_DIRECTORY3_DIRECTORY4_DIRECTORY5_FUNC2_H
#define SYS1_DIRECTORY1A_DIRECTORY2_DIRECTORY3_DIRECTORY4_DIRECTORY5_FUNC2_H

void func2();

#endif  // SYS1_DIRECTORY1A_DIRECTORY2_DIRECTORY3_DIRECTORY4_DIRECTORY5_FUNC2_H

$ cat directory1b/directory2/directory3/directory4/directory5/func4.h
#ifndef DIRECTORY1B_DIRECTORY2_DIRECTORY3_DIRECTORY4_DIRECTORY5_FUNC4_H
#define DIRECTORY1B_DIRECTORY2_DIRECTORY3_DIRECTORY4_DIRECTORY5_FUNC4_H

void func4();

#endif  // DIRECTORY1B_DIRECTORY2_DIRECTORY3_DIRECTORY4_DIRECTORY5_FUNC4_H
```

Make sure that the width of guard lines does not go over 40 columns, by using a hash:

```bash
$ header_guardian --nameroot . -r directory1b --width 40

$ cat directory1b/directory2/directory3/directory4/directory5/func3.h 
#ifndef HASH_E31CC83282930C6D2EB2A91C26ABFDE3
#define HASH_E31CC83282930C6D2EB2A91C26ABFDE3

void func3();

#endif  // HASH_E31CC83282930C6D2EB2A91C26ABFDE3

$ cat directory1b/directory2/directory3/directory4/directory5/func4.h 
#ifndef HASH_13EF278DE3829713E022DF6000B9CD74
#define HASH_13EF278DE3829713E022DF6000B9CD74

void func4();

#endif  // HASH_13EF278DE3829713E022DF6000B9CD74
```
